<?php
/**
 * Regression test for the ad-network money rules (economy.php + click_recorder.php).
 *   php test_economy.php
 * Uses a throwaway ad and advertiser (fake addresses, fake visitor IPs 203.0.113.x) and removes everything it creates.
 */
chdir(__DIR__);
error_reporting(E_ALL & ~E_WARNING);
$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36';
require __DIR__ . '/click_recorder.php';
$pdo = new PDO("mysql:host=localhost;dbname=adnetwrk;charset=utf8mb4", 'root', '', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);

const AD = 'test-ad-econ';
const ADV = 'NTESTADVERTISER000000000000000000';
$fails = 0;
function check($label, $cond, $detail = '') { global $fails; echo ($cond ? "  ok    " : "  FAIL  ") . $label . ($detail !== '' ? "   [$detail]" : "") . "\n"; if (!$cond) $fails++; }
function visitor($n) { $_SERVER['REMOTE_ADDR'] = "203.0.113.$n"; array_map('unlink', glob(sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'pyc_ratelimit' . DIRECTORY_SEPARATOR . '*.json') ?: []); }
function bal($pdo) { return econ_balance_sat($pdo, ADV); }
function click($pdo, $dev) { return clk_record_click($pdo, ['ad_id' => AD, 'client_id' => 'storage', 'zone' => 'z', 'developer_address' => $dev, 'load_id' => bin2hex(random_bytes(12))], 'test'); }

$meta = __DIR__ . '/ads_storage/active/' . AD . '_meta.json';
function writeAd($advertiser, $budget = 0.0025, $maxClicks = 5, $payout = 0.001) {
    global $meta;
    file_put_contents($meta, json_encode(['id' => AD, 'status' => 'active', 'payout_amount' => $payout, 'advertiser_address' => $advertiser,
        'expires_at' => date('c', time() + 86400), 'targeting' => ['budget_daily' => $budget, 'max_clicks_daily' => $maxClicks]]));
}
function cleanup($pdo) {
    global $meta;
    @unlink($meta);
    $pdo->prepare("DELETE FROM ad_clicks WHERE ad_id = ?")->execute([AD]);
    $pdo->prepare("DELETE FROM ad_approvals WHERE ad_id = ?")->execute([AD]);
    $pdo->prepare("DELETE FROM advertiser_ledger WHERE address = ?")->execute([ADV]);
    $pdo->prepare("DELETE FROM advertiser_accounts WHERE address = ?")->execute([ADV]);
}
cleanup($pdo);

$dev = $pdo->query("SELECT pythoncoin_address FROM developers WHERE id = 2")->fetchColumn();   // a publisher that is not the advertiser
$devSelf = $dev;
writeAd(ADV);

echo "approval and funding\n";
visitor(1);
$r = click($pdo, $dev);
check("an ad nobody has approved is refused", !$r['ok'] && $r['error'] === 'Ad is not approved', $r['error']);
check("...and it is queued for review", $pdo->query("SELECT status FROM ad_approvals WHERE ad_id='" . AD . "'")->fetchColumn() === 'pending');
$pdo->exec("UPDATE ad_approvals SET status='approved' WHERE ad_id='" . AD . "'");
visitor(1);
$r = click($pdo, $dev);
check("an approved ad whose advertiser has no funds is refused", !$r['ok'] && $r['error'] === 'Advertiser out of funds', $r['error']);
[$ok, $why] = econ_ad_serveable($pdo, ['id' => AD, 'advertiser' => ADV, 'payout' => 0.001, 'daily_budget' => 0.0025, 'max_clicks' => 5]);
check("an unfunded ad is not served to publishers", !$ok && $why === 'advertiser out of funds', $why);

$pdo->prepare("INSERT INTO advertiser_accounts (address, balance_sat, deposited_sat) VALUES (?, ?, ?)")->execute([ADV, 1000000, 1000000]);   // 0.01 funded, but the daily budget is only 0.0025
[$ok] = econ_ad_serveable($pdo, ['id' => AD, 'advertiser' => ADV, 'payout' => 0.001, 'daily_budget' => 0.0025, 'max_clicks' => 5]);
check("once funded and approved the ad is served", $ok);

echo "\ncharging and the hold period\n";
visitor(2);
$r = click($pdo, $dev);
check("a click on a funded, approved ad is recorded", $r['ok'] && $r['amount'] === 0.001, json_encode($r['error']));
$row = $pdo->query("SELECT * FROM ad_clicks WHERE id = " . (int)$r['id'])->fetch();
check("the advertiser was charged exactly the payout (at cost, 0% fee)", bal($pdo) === 900000 && (int)$row['charged_sat'] === 100000, "balance=" . bal($pdo));
check("the click names who paid", $row['advertiser_address'] === ADV);
check("the ledger shows the charge", (int)$pdo->query("SELECT amount_sat FROM advertiser_ledger WHERE address='" . ADV . "' AND kind='click'")->fetchColumn() === -100000);
$hold = $pdo->query("SELECT TIMESTAMPDIFF(MINUTE, NOW(), payable_after) FROM ad_clicks WHERE id = " . (int)$r['id'])->fetchColumn();
check("the click is not payable for about 24 hours", $hold >= 1430 && $hold <= 1440, "minutes=$hold");
visitor(3);
$r = click($pdo, $dev);
check("a second click is recorded", $r['ok']);
check("balance after two clicks", bal($pdo) === 800000, (string)bal($pdo));
visitor(4);
$r = click($pdo, $dev);
check("a third click would exceed the daily budget (0.0025) and is refused", !$r['ok'] && $r['error'] === 'Daily budget used up', $r['error']);
check("a refused click costs the advertiser nothing", bal($pdo) === 800000);
[$ok, $why] = econ_ad_serveable($pdo, ['id' => AD, 'advertiser' => ADV, 'payout' => 0.001, 'daily_budget' => 0.0025, 'max_clicks' => 5]);
check("the ad stops being served when its budget is used up", !$ok && $why === 'daily budget used up', $why);

echo "\nfraud rules\n";
visitor(5);
writeAd($dev);                                   // now the advertiser is the publisher itself
$r = click($pdo, $dev);
check("an advertiser cannot earn from its own ad", !$r['ok'] && strpos($r['error'], 'own ads') !== false, $r['error']);
writeAd(ADV, 100.0, 5);
$_SERVER['HTTP_USER_AGENT'] = 'python-requests/2.32 click-farm';
visitor(6);
$r = click($pdo, $dev);
check("clicks from scripts and bots are refused", !$r['ok'] && strpos($r['error'], 'automated') !== false, $r['error']);
$_SERVER['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36';
visitor(7);
for ($i = 0; $i < 3; $i++) {
    $pdo->prepare("INSERT INTO ad_clicks (username, ad_id, ip_address, developer_id, developer_address, payout_amount, processed, payment_status, advertiser_address, charged_sat) VALUES ('x', ?, '203.0.113.7', 2, ?, 0.001, 0, 'test', ?, 0)")->execute([AD, $dev, ADV]);
}
$before = bal($pdo);
$r = click($pdo, $dev);
check("one visitor is limited to 3 paid clicks per ad per day", !$r['ok'] && strpos($r['error'], 'this ad') !== false, $r['error']);
$pdo->exec("UPDATE ad_clicks SET charged_sat = 0 WHERE ad_id='" . AD . "' AND ip_address='203.0.113.7'");


echo "\none click per page load\n";
$pdo->prepare("UPDATE advertiser_accounts SET balance_sat = 100000000 WHERE address = ?")->execute([ADV]);
writeAd(ADV, 100.0, 50);
$load = bin2hex(random_bytes(12));
$one = function ($lid) use ($pdo, $dev) { return clk_record_click($pdo, ['ad_id' => AD, 'client_id' => 'storage', 'zone' => 'z', 'developer_address' => $dev, 'load_id' => $lid], 'test'); };
visitor(8);
$r = $one($load);
check("the first click of a page load is paid", $r['ok'], $r['error']);
visitor(8);
$r = $one($load);
check("a second click in the same page load is refused", !$r['ok'] && strpos($r['error'], 'page load') !== false, $r['error']);
visitor(8);
$r = $one('');
check("a click without a page-load id is refused", !$r['ok'] && strpos($r['error'], 'page-load') !== false, $r['error']);
visitor(9);
$r = $one(bin2hex(random_bytes(12)));
check("a new page load can click again", $r['ok'], $r['error']);
$pdo->exec("DELETE FROM ad_clicks WHERE ad_id='" . AD . "' AND payment_status='test'");
echo "\nsafety\n";
$pdo->prepare("UPDATE advertiser_accounts SET balance_sat = 100000 WHERE address = ?")->execute([ADV]);
$res = econ_charge_and_insert($pdo, ADV, AD, 100000, ['max_clicks' => null, 'daily_budget' => null], ['username' => 'x', 'ad_id' => AD, 'no_such_column' => 1]);
check("if recording the click fails, the charge is rolled back", !$res['ok'] && bal($pdo) === 100000, "balance=" . bal($pdo));
check("a 10% network fee would be charged on top of the publisher's payout", econ_charge_sat(100000, 10) === 110000 && econ_charge_sat(100000, 0) === 100000);
check("an unknown / invented ad id is refused", !clk_record_click($pdo, ['ad_id' => 'not-a-real-ad', 'developer_address' => $dev], 'test')['ok']);

cleanup($pdo);
check("test data removed", (int)$pdo->query("SELECT COUNT(*) FROM ad_clicks WHERE ad_id='" . AD . "'")->fetchColumn() === 0 && !file_exists($meta));
echo $fails === 0 ? "\nALL PASSED\n" : "\n$fails FAILED\n";
exit($fails === 0 ? 0 : 1);

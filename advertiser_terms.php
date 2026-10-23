<?php
/**
 * Advertiser Agreement page: anyone who wants to submit ads reads and accepts the current terms here first.
 * Acceptance is stored against their wallet address; submit_ad.php refuses ads from addresses that have not accepted the
 * current version.
 */
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/agreements.php';
require_once __DIR__ . '/btcshop_bridge.php';

session_start();
header('X-Frame-Options: DENY');
header("Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'");
header('Referrer-Policy: no-referrer');

$terms = agr_current_terms();
$coin = agr_coin();
$fee = bridge_fee_info();
$h = function ($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); };
$message = ''; $ok = false;
if (empty($_SESSION['agr_csrf'])) $_SESSION['agr_csrf'] = bin2hex(random_bytes(16));

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $address = trim((string)($_POST['address'] ?? ''));
    $name = trim((string)($_POST['name'] ?? ''));
    $email = trim((string)($_POST['email'] ?? ''));
    if (!hash_equals($_SESSION['agr_csrf'], (string)($_POST['csrf'] ?? ''))) {
        $message = 'This form expired. Please reload the page and try again.';
    } elseif (!sec_rate_limit('accept_terms', 10, 3600)) {
        $message = 'Too many attempts. Please try again later.';
    } elseif (empty($_POST['agree'])) {
        $message = 'You must tick the box to accept the agreement.';
    } elseif ($name === '' || mb_strlen($name) > 200) {
        $message = 'Please enter your name or your organisation\'s name.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $message = 'Please enter a valid e-mail address.';
    } elseif (!agr_address_valid($address)) {
        $message = 'That is not a valid ' . $coin['coin_name'] . ' wallet address.';
    } else {
        try {
            agr_record(pyc_pdo(), $address, $terms['version'], $name, $email, 'web');
            $ok = true;
        } catch (Throwable $e) {
            error_log('advertiser_terms: ' . $e->getMessage());
            $message = 'Sorry, your acceptance could not be saved. Please try again later.';
        }
    }
}
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= $h($terms['title']) ?> - <?= $h($coin['coin_name']) ?></title>
<style>
:root{color-scheme:light dark;--bg:#fff;--fg:#1c2230;--mut:#5b6577;--line:#d9deea;--card:#f6f8fc;--acc:#2456d6;--ok:#14803c;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root{--bg:#10141d;--fg:#e8ecf5;--mut:#9aa6bd;--line:#273049;--card:#171d2b;--acc:#7aa2ff;--ok:#5bd68a;--bad:#ff8a80}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:46rem;margin:0 auto;padding:1.5rem 1rem 4rem}
h1{font-size:1.6rem;margin:.2rem 0}.meta{color:var(--mut);font-size:.9rem}
h2{font-size:1.05rem;margin:1.4rem 0 .3rem}p{margin:.3rem 0}
.box{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.9rem 1rem;margin:1rem 0}
.steps li{margin:.35rem 0}
label{display:block;margin:.7rem 0 .2rem;font-weight:600}
input[type=text],input[type=email]{width:100%;box-sizing:border-box;padding:.5rem .6rem;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit}
button{margin-top:1rem;padding:.6rem 1.2rem;border:0;border-radius:6px;background:var(--acc);color:#fff;font:inherit;font-weight:600;cursor:pointer}
.agree{display:flex;gap:.6rem;align-items:flex-start;margin-top:1rem;font-weight:400}.agree input{margin-top:.3rem}
.err{color:var(--bad);font-weight:600}.good{color:var(--ok);font-weight:600}code{background:var(--card);padding:.1rem .3rem;border-radius:4px}
</style></head><body><main>
<h1><?= $h($terms['title']) ?></h1>
<div class="meta"><?= $h($coin['coin_name']) ?> ad network &middot; version <?= (int)$terms['version'] ?> &middot; effective <?= $h($terms['effective']) ?></div>

<?php if ($ok): ?>
  <div class="box"><p class="good">Thank you - your acceptance of version <?= (int)$terms['version'] ?> is recorded for <code><?= $h($address) ?></code>.</p>
  <p>Next steps:</p>
  <ol class="steps">
    <?php if ($fee['required']): ?>
    <li><b>Pay the upload fee</b><?= $fee['btc'] !== null ? ' (' . $h($fee['btc']) . ' BTC per ad)' : '' ?> in the Operator's shop<?= $fee['shop_url'] !== '' ? ': <code>' . $h($fee['shop_url']) . '</code>' : '' ?>. Buy the <i>Ad upload</i> item and note your <b>order number</b> and <b>secure ID</b>.</li>
    <?php endif; ?>
    <li><b>Send your ad</b> from the wallet app (it signs the submission with your wallet key<?= $fee['required'] ? ' and includes your order number and secure ID' : '' ?>).</li>
    <li>We review it. Once approved and your advertiser balance has funds, it goes live.</li>
  </ol></div>
<?php else: ?>
  <?php if ($message !== ''): ?><p class="err"><?= $h($message) ?></p><?php endif; ?>
  <div class="box">
    <b>Before you submit an ad:</b>
    <ol class="steps">
      <li>Read the agreement below and accept it with your wallet address.</li>
      <?php if ($fee['required']): ?><li>Pay the upload fee in the Operator's shop (<?= $fee['btc'] !== null ? $h($fee['btc']) . ' BTC per ad' : 'price shown in the shop' ?>). Uploading and hosting your ad content is a paid service and is required for every submission.</li><?php endif; ?>
      <li>Fund your advertiser balance by sending <?= $h($coin['ticker']) ?> to the network wallet.</li>
    </ol>
  </div>
  <?php foreach ($terms['sections'] as $s): ?>
    <h2><?= $h($s['heading']) ?></h2>
    <?php foreach (explode("\n", trim($s['body'])) as $line): ?><p><?= $h($line) ?></p><?php endforeach; ?>
  <?php endforeach; ?>

  <form method="post" class="box" autocomplete="off">
    <b>Accept this agreement</b>
    <input type="hidden" name="csrf" value="<?= $h($_SESSION['agr_csrf']) ?>">
    <label for="name">Your name or organisation</label><input type="text" id="name" name="name" maxlength="200" required value="<?= $h($_POST['name'] ?? '') ?>">
    <label for="email">E-mail address</label><input type="email" id="email" name="email" maxlength="200" required value="<?= $h($_POST['email'] ?? '') ?>">
    <label for="address">Your <?= $h($coin['coin_name']) ?> wallet address</label><input type="text" id="address" name="address" maxlength="40" required value="<?= $h($_POST['address'] ?? '') ?>">
    <label class="agree"><input type="checkbox" name="agree" value="1"> <span>I have read and I accept this agreement (version <?= (int)$terms['version'] ?>) for this wallet address.</span></label>
    <button type="submit">I accept</button>
  </form>
<?php endif; ?>
</main></body></html>

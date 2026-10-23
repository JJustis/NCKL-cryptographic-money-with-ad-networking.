<?php
/**
 * Shared pieces of the public pages (index.php, learn.php): security headers, the page frame, and live network figures.
 * Pages are static HTML + one stylesheet + one tiny script; nothing is loaded from other websites.
 */
require_once __DIR__ . '/dbconfig.php';

function site_h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

function site_cfg() {
    $site = pyc_read_json_config('site_config.json', []);
    $coin = pyc_read_json_config('consensus_params.json', ['coin_name' => 'Nickles', 'ticker' => 'NCKL']);
    return [
        'coin' => $coin['coin_name'] ?? 'Nickles',
        'ticker' => $coin['ticker'] ?? 'NCKL',
        'base' => rtrim($site['base_url'] ?? '', '/'),
        'operator' => $site['operator_name'] ?? '',
        'contact' => $site['operator_contact'] ?? '',
        'repo' => $site['github_url'] ?? 'https://github.com/JJustis/NCKL-cryptographic-money-with-ad-networking.',
        'repo_zip' => ($site['github_url'] ?? 'https://github.com/JJustis/NCKL-cryptographic-money-with-ad-networking.') . '/archive/refs/heads/main.zip',
        'repo_clone' => ($site['github_url'] ?? 'https://github.com/JJustis/NCKL-cryptographic-money-with-ad-networking.') . '.git',
    ];
}

function site_headers() {
    header("Content-Security-Policy: default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('Permissions-Policy: camera=(), microphone=(), geolocation=()');
}

/** The brand coin: a simple "N" on a nickel-coloured disc (inline SVG, no image file needed). */
function site_coin($size = 36) {
    static $n = 0; $n++;
    $s = (int)$size; $id = 'nk' . $n;
    return '<svg class="coin" width="' . $s . '" height="' . $s . '" viewBox="0 0 64 64" role="img" aria-label="Nickles coin">'
         . '<defs><linearGradient id="' . $id . '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef2f7"/><stop offset=".55" stop-color="#b9c3d1"/><stop offset="1" stop-color="#8b97a9"/></linearGradient></defs>'
         . '<circle cx="32" cy="32" r="30" fill="url(#' . $id . ')" stroke="#6f7c90" stroke-width="2"/>'
         . '<circle cx="32" cy="32" r="24" fill="none" stroke="#6f7c90" stroke-width="1.2" stroke-dasharray="2 3"/>'
         . '<path d="M21 45V19h5.2l11.6 17.6V19H43v26h-5.1L26.2 27.3V45z" fill="#26364d"/></svg>';
}

function site_head($title, $desc, $active = '') {
    $c = site_cfg();
    site_headers();
    $url = $c['base'] !== '' ? $c['base'] . '/' . ($active === 'learn' ? 'learn.php' : '') : '';
    $nav = [['index.php#start', 'Get started', 'start'], ['index.php#roles', 'Who it\'s for', 'roles'], ['learn.php', 'Learn', 'learn'], ['index.php#faq', 'FAQ', 'faq']];
    echo "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n";
    echo '<title>' . site_h($title) . "</title>\n";
    echo '<meta name="description" content="' . site_h($desc) . "\">\n";
    echo '<meta property="og:type" content="website"><meta property="og:title" content="' . site_h($title) . '"><meta property="og:description" content="' . site_h($desc) . "\">\n";
    if ($url !== '') echo '<link rel="canonical" href="' . site_h($url) . '"><meta property="og:url" content="' . site_h($url) . "\">\n";
    echo '<meta name="theme-color" content="#1f3a5f">' . "\n";
    echo '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Ccircle cx=%2732%27 cy=%2732%27 r=%2730%27 fill=%27%23b9c3d1%27 stroke=%27%236f7c90%27 stroke-width=%272%27/%3E%3Cpath d=%27M21 45V19h5.2l11.6 17.6V19H43v26h-5.1L26.2 27.3V45z%27 fill=%27%2326364d%27/%3E%3C/svg%3E">' . "\n";
    echo '<link rel="stylesheet" href="site.css"></head><body>' . "\n";
    echo '<a class="skip" href="#main">Skip to content</a>' . "\n";
    echo '<header class="top"><div class="wrap bar"><a class="brand" href="index.php">' . site_coin(34) . '<span>' . site_h($c['coin']) . ' <small>' . site_h($c['ticker']) . '</small></span></a>';
    echo '<input type="checkbox" id="navtoggle" class="navtoggle" aria-label="Toggle menu"><label for="navtoggle" class="burger" aria-hidden="true"><span></span></label>';
    echo '<nav class="nav" aria-label="Main">';
    foreach ($nav as [$href, $label, $key]) echo '<a href="' . site_h($href) . '"' . ($active === $key ? ' aria-current="page"' : '') . '>' . site_h($label) . '</a>';
    echo '<a class="btn btn-ghost" href="' . site_h($c['repo']) . '" rel="noopener">GitHub</a></nav></div></header>' . "\n<main id=\"main\">\n";
}

function site_foot() {
    $c = site_cfg();
    echo "</main>\n<footer class=\"foot\"><div class=\"wrap foot-grid\">";
    echo '<div><div class="brand brand-foot">' . site_coin(30) . '<span>' . site_h($c['coin']) . '</span></div><p class="muted">A fair-launch, proof-of-work coin with a built-in ad network. Open source under the MIT licence.</p><p class="muted">Official website: <a href="' . site_h($c['base'] !== '' ? $c['base'] . '/' : 'index.php') . '">' . site_h(preg_replace('#^https?://#', '', $c['base'] !== '' ? $c['base'] : 'this site')) . '</a></p></div>';
    echo '<div><h3>Explore</h3><ul><li><a href="learn.php">Learn about ' . site_h($c['coin']) . '</a></li><li><a href="index.php#start">Get started</a></li><li><a href="index.php#faq">FAQ</a></li></ul></div>';
    echo '<div><h3>Use the network</h3><ul><li><a href="dashboard8.php">Publisher dashboard</a></li><li><a href="advertiser_terms.php">Advertiser agreement</a></li><li><a href="developer_portal.html">Developer portal</a></li></ul></div>';
    echo '<div><h3>Source &amp; docs</h3><ul><li><a href="' . site_h($c['repo']) . '" rel="noopener">GitHub repository</a></li><li><a href="' . site_h($c['repo']) . '/blob/main/CONSENSUS.md" rel="noopener">Consensus rules</a></li><li><a href="' . site_h($c['repo']) . '/blob/main/ECONOMY.md" rel="noopener">Ad economy</a></li></ul></div>';
    echo "</div>\n<div class=\"wrap legal\"><p>" . site_h($c['coin']) . ' (' . site_h($c['ticker']) . ') is experimental software. Coins have no guaranteed value and nothing here is financial, legal or investment advice. Use it only with amounts you can afford to lose.';
    if ($c['operator'] !== '') echo ' Operated by ' . site_h($c['operator']) . ($c['contact'] !== '' ? ' &middot; ' . site_h($c['contact']) : '') . '.';
    echo "</p></div></footer>\n<script src=\"site.js\" defer></script>\n</body></html>";
}

/** Reward (in coins) of the block that comes after `$height`. */
function site_next_reward($height) {
    $halvings = intdiv($height + 1, 210000);
    return $halvings >= 64 ? 0 : 50 / (2 ** $halvings);
}

/** Coins created so far by blocks 1..$height. */
function site_issued($height) {
    $total = 0.0; $left = $height; $reward = 50.0;
    while ($left > 0 && $reward >= 1e-8) {
        $n = min($left, 210000);
        $total += $n * $reward;
        $left -= $n; $reward /= 2;
    }
    return $total;
}

/** Live figures for the home page (cached 30 s). Aggregates only; nothing private. */
function site_stats() {
    $cache = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'nickles_site_stats.json';
    if (is_file($cache) && filemtime($cache) > time() - 30) {
        $c = json_decode((string)file_get_contents($cache), true);
        if (is_array($c)) return $c;
    }
    $s = ['height' => null, 'issued' => null, 'reward' => null, 'to_halving' => null, 'ads' => 0, 'publishers' => null, 'updated' => date('c')];
    $chain = __DIR__ . '/blockchain.json';
    if (is_file($chain) && filesize($chain) < 60 * 1024 * 1024) {
        $j = json_decode((string)file_get_contents($chain), true);
        if (is_array($j) && isset($j['chain']) && is_array($j['chain'])) {
            $h = max(0, count($j['chain']) - 1);
            $s['height'] = $h; $s['issued'] = site_issued($h); $s['reward'] = site_next_reward($h);
            $s['to_halving'] = 210000 - (($h + 1) % 210000);
        }
    }
    foreach (glob(__DIR__ . '/ads_storage/active/*_meta.json') ?: [] as $f) {
        $m = json_decode((string)file_get_contents($f), true);
        if (is_array($m) && (($m['status'] ?? 'active') === 'active') && (empty($m['expires_at']) || strtotime($m['expires_at']) > time())) $s['ads']++;
    }
    try {
        $pdo = pyc_pdo();
        $s['publishers'] = (int)$pdo->query('SELECT COUNT(*) FROM developers')->fetchColumn();
    } catch (Throwable $e) { /* the page works without the database */ }
    @file_put_contents($cache, json_encode($s));
    return $s;
}

function site_num($n, $dec = 0) { return $n === null ? '&ndash;' : number_format((float)$n, $dec); }

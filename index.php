<?php
require_once __DIR__ . '/site_common.php';
$c = site_cfg();
$st = site_stats();
$coin = site_h($c['coin']); $tick = site_h($c['ticker']);
site_head($c['coin'] . ' (' . $c['ticker'] . ') - a fair-launch coin with a built-in ad network',
          'Nickles is an open-source, Bitcoin-style coin with a built-in pay-per-click ad network. Mine it, earn it by showing ads, or advertise with it. Start here.', 'home');
?>
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Fair launch &middot; Proof of work &middot; Open source</span>
      <h1>A coin you can mine &mdash; and earn by showing ads.</h1>
      <p class="lead"><?= $coin ?> (<?= $tick ?>) is a Bitcoin-style digital coin with a pay-per-click advertising network built in. Advertisers pay for real clicks, website owners earn them, and miners keep the chain honest. No pre-mine, no sign-up, no middleman holding your money.</p>
      <div class="cta">
        <a class="btn btn-primary" href="#start">Get started in 5 minutes</a>
        <a class="btn btn-ghost" href="learn.php">Learn how it works</a>
        <a class="btn btn-ghost" href="<?= site_h($c['repo']) ?>" rel="noopener">View on GitHub</a>
      </div>
      <p class="fine">New to crypto? That's fine &mdash; the setup wizard explains everything as it goes, and the <a href="learn.php">guide</a> covers the basics in plain language.</p>
    </div>

    <aside class="panel" aria-label="Network status">
      <div class="panel-head"><span>Network status</span><span class="live">Live</span></div>
      <div class="stats">
        <div class="stat"><b><?= site_num($st['height']) ?></b><span>Block height</span></div>
        <div class="stat"><b><?= site_num($st['issued'], 0) ?></b><span><?= $tick ?> issued of 21,000,000</span></div>
        <div class="stat"><b><?= site_num($st['reward'], 2) ?></b><span><?= $tick ?> per block now</span></div>
        <div class="stat"><b><?= site_num($st['to_halving']) ?></b><span>Blocks to next halving</span></div>
        <div class="stat"><b><?= site_num($st['ads']) ?></b><span>Ads live</span></div>
        <div class="stat"><b><?= site_num($st['publishers']) ?></b><span>Publishers</span></div>
      </div>
      <p class="panel-note">The network launched on 23 October 2026 from a block with zero coins. Early days: expect a small, young network.</p>
    </aside>
  </div>
</section>

<div class="wrap"><div class="trust" role="list">
  <span role="listitem">21,000,000 coin cap</span><span role="listitem">Zero pre-mine</span><span role="listitem">Halving every 210,000 blocks</span>
  <span role="listitem">Encrypted API</span><span role="listitem">MIT open source</span>
</div></div>

<section id="start">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">New here? Start here</span><h2>From zero to running in three steps</h2>
      <p>You don't need to know anything about crypto. Follow these in order.</p></div>
    <div class="grid g3">
      <div class="card"><div class="num">1</div><h3>Understand the basics</h3><p>Five minutes on what a coin, a wallet and mining are, and what makes <?= $coin ?> different. Plain language, no jargon.</p><a class="more" href="learn.php">Read the guide &rarr;</a></div>
      <div class="card"><div class="num">2</div><h3>Install it</h3><p>Download the program and double-click <code>setup.bat</code>. The wizard checks your PC, installs what is missing, creates your wallet and sets everything up.</p><a class="more" href="#install">See the install steps &rarr;</a></div>
      <div class="card"><div class="num">3</div><h3>Pick what you want to do</h3><p>Mine coins, earn from ads on your website, or advertise your own business. You can do more than one.</p><a class="more" href="#roles">Choose your role &rarr;</a></div>
    </div>
  </div>
</section>

<section id="roles" class="alt">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">Who it's for</span><h2>Four ways to take part</h2><p>Everything runs on the same coin and the same rules.</p></div>
    <div class="grid g4">
      <article class="card"><div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg></div>
        <h3>Publisher</h3><p>You own a website or app and want to earn from it.</p>
        <ul><li>Paste one snippet of code on your page</li><li>Earn <?= $tick ?> for every genuine click</li><li>Paid to your own wallet</li></ul>
        <a class="more" href="dashboard8.php">Open the dashboard &rarr;</a></article>
      <article class="card"><div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg></div>
        <h3>Advertiser</h3><p>You want real visitors for your business.</p>
        <ul><li>Accept the short agreement</li><li>Submit your ad; it is reviewed first</li><li>Pay only for clicks, at cost</li></ul>
        <a class="more" href="advertiser_terms.php">Read the agreement &rarr;</a></article>
      <article class="card"><div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg></div>
        <h3>Miner</h3><p>You'd like to earn <?= $tick ?> by securing the network.</p>
        <ul><li>The wallet app mines for you</li><li>50 <?= $tick ?> per block to start</li><li>Reward halves every 210,000 blocks</li></ul>
        <a class="more" href="learn.php#mining">How mining works &rarr;</a></article>
      <article class="card"><div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/></svg></div>
        <h3>Developer</h3><p>You want to read, test or build on it.</p>
        <ul><li>Python, PHP and plain JavaScript</li><li>Consensus rules and tests included</li><li>MIT licence: use it freely</li></ul>
        <a class="more" href="<?= site_h($c['repo']) ?>" rel="noopener">Browse the source &rarr;</a></article>
    </div>
  </div>
</section>

<section id="how">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">How the money moves</span><h2>One click, five steps</h2>
      <p>Every payment is an ordinary <?= $tick ?> transaction on the shared chain, so it can be checked by anyone.</p></div>
    <ol class="flow">
      <li><b>Advertiser funds a balance</b><span>Sends <?= $tick ?> to the network wallet; it counts after 6 confirmations.</span></li>
      <li><b>A visitor clicks an ad</b><span>On a publisher's site. One paid click per page load.</span></li>
      <li><b>The click is charged</b><span>The advertiser's balance drops by the click price, at cost.</span></li>
      <li><b>24-hour hold</b><span>Bots, self-clicks and fraud are filtered before anyone is paid.</span></li>
      <li><b>Publisher is paid</b><span>A normal <?= $tick ?> transaction to the publisher's wallet.</span></li>
    </ol>
    <p class="muted mt">Nothing is shown until a person has approved the ad, and each ad is labelled &ldquo;Ad&rdquo; and runs in a sandbox so it cannot touch the page around it.</p>
  </div>
</section>

<section id="install" class="alt">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">Quick start</span><h2>Install on Windows in five steps</h2>
      <p>Built for Windows 10 and 11. You need about 1&nbsp;GB of free disk space and an internet connection for the first run.</p></div>
    <ol class="steps">
      <li><div><h3>Download the program</h3>
        <p>Download the ZIP from GitHub and unzip it, or clone it if you use git. It is open source; you can read every file.</p>
        <p><a class="btn btn-primary" href="<?= site_h($c['repo_zip']) ?>" rel="noopener">Download ZIP</a></p>
        <pre class="code">git clone <?= site_h($c['repo_clone']) ?></pre></div></li>
      <li><div><h3>Double-click <code>setup.bat</code></h3>
        <p>The wizard starts. It first explains how <?= $coin ?> works in three short screens, then checks your PC, installs Python packages, and offers to install XAMPP (the free web server and database it needs) if you don't have it.</p>
        <div class="note"><p><strong>Back up your wallet.</strong> The wizard creates <code>wallet.json</code> &mdash; it holds your private key. If you lose it, your coins are gone, and nobody can recover them for you.</p></div></div></li>
      <li><div><h3>Start the wallet</h3>
        <p>Run <code>run.bat</code>. It opens the wallet and node, starts the database and web server if needed, and shows your address (it starts with <code>N</code>).</p></div></li>
      <li><div><h3>Mine your first coins</h3>
        <p>Open the mining tab and press start. New coins can be spent after 100 further blocks, so be patient on a young network.</p></div></li>
      <li><div><h3>Put the network to work</h3>
        <p><strong>Publishers:</strong> sign in to the <a href="dashboard8.php">dashboard</a> with your wallet address and copy the ad code into your page. <strong>Advertisers:</strong> accept the <a href="advertiser_terms.php">agreement</a>, pay the one-time upload fee, and submit your ad from the wallet app.</p></div></li>
    </ol>
  </div>
</section>

<section id="facts">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">The coin at a glance</span><h2>Key facts</h2></div>
    <div class="tbl-wrap"><table>
      <tbody>
        <tr><td>Name / ticker</td><td><?= $coin ?> / <?= $tick ?></td></tr>
        <tr><td>Maximum supply</td><td>21,000,000 <?= $tick ?> &mdash; enforced by every node</td></tr>
        <tr><td>Pre-mine</td><td>None. The first block creates no coins; every coin is mined.</td></tr>
        <tr><td>Consensus</td><td>Proof of work (SHA-256), blocks about every 10 minutes, difficulty adjusts every 2,016 blocks</td></tr>
        <tr><td>Block reward</td><td>50 <?= $tick ?>, halving every 210,000 blocks; usable after 100 blocks</td></tr>
        <tr><td>Addresses</td><td>Start with <code>N</code> (so they can't be confused with Bitcoin addresses)</td></tr>
        <tr><td>Network ports</td><td>8333 (peer-to-peer), 8332 (ad portal)</td></tr>
        <tr><td>Advertising</td><td>Pay-per-click, charged at cost; ads are reviewed; clicks held 24 hours</td></tr>
        <tr><td>Licence</td><td>MIT &mdash; free to use, study and modify</td></tr>
      </tbody></table></div>
  </div>
</section>

<section id="trust" class="alt">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">Straight talk</span><h2>What's built in &mdash; and what to be careful about</h2></div>
    <div class="grid g2">
      <div class="card"><h3>Protections in place</h3>
        <ul><li>Rules enforced in code: no node accepts a block that pays itself extra</li><li>Encrypted requests between the wallet, websites and server</li><li>Ads reviewed by a person and sandboxed before they are shown</li><li>Bot filtering, per-visitor limits and a 24-hour hold on payouts</li><li>Secrets (wallet, keys, database login) are never served by the web server</li></ul></div>
      <div class="card"><h3>Be honest with yourself</h3>
        <ul><li><?= $coin ?> is brand new and experimental software, not independently audited</li><li>Coins have <strong>no guaranteed value</strong> and there is no exchange; this is not an investment</li><li>Back up your wallet and keep your private key secret</li><li>The advertiser agreement is a template &mdash; operators should have a lawyer check it</li><li>Rules for crypto and advertising differ by country; check yours</li></ul></div>
    </div>
  </div>
</section>

<section id="faq">
  <div class="wrap">
    <div class="sec-head"><span class="kicker">FAQ</span><h2>Questions people ask</h2></div>
    <div>
      <details><summary>Does installing create a new coin each time?</summary><p>No. Every install starts from the same first block, so everyone shares one coin and one chain. Coins are only created as block rewards, and every node rejects a block that pays out more than the rules allow. <a href="learn.php#supply">More on the supply rules.</a></p></details>
      <details><summary>Is it a copy of Bitcoin?</summary><p>It borrows Bitcoin's proven ideas &mdash; fixed supply, halving, proof of work, unspent-output accounting &mdash; but it is separate software with its own chain, its own address style and a built-in ad network.</p></details>
      <details><summary>How much will my coins be worth?</summary><p>Nobody can say, and nothing is promised. Treat <?= $tick ?> as an experiment, not an investment.</p></details>
      <details><summary>Do I need to create an account?</summary><p>No. Your wallet address is your identity. There are no passwords or sign-up forms to leak.</p></details>
      <details><summary>How do publishers get paid?</summary><p>Clicks are held for 24 hours to catch fraud, then paid to the publisher's wallet address as a normal <?= $tick ?> transaction by the network operator's wallet.</p></details>
      <details><summary>Why is there an upload fee for advertisers?</summary><p>Hosting and reviewing each ad costs the operator time and storage. The fee is paid once per submission in Bitcoin through the operator's shop; clicks themselves are paid in <?= $tick ?>.</p></details>
      <details><summary>What if I lose my wallet file?</summary><p>The coins are gone for good. Copy <code>wallet.json</code> to a safe place (a USB stick, an encrypted drive) as soon as it's created.</p></details>
      <details><summary>Can I run it on Mac or Linux?</summary><p>The code is Python and PHP, so it can run elsewhere, but the one-click wizard (<code>setup.bat</code>) is for Windows. Developers are welcome to help port it.</p></details>
      <details><summary>Where can I report a bug or a security problem?</summary><p>Open an issue on <a href="<?= site_h($c['repo']) ?>/issues" rel="noopener">GitHub</a>. For a security problem, please describe it without publishing exploit details.</p></details>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap center">
    <h2>Ready to try it?</h2>
    <p class="lead">Download, run the wizard, and you're part of the network in a few minutes.</p>
    <div class="cta">
      <a class="btn btn-primary" href="<?= site_h($c['repo_zip']) ?>" rel="noopener">Download ZIP</a>
      <a class="btn btn-ghost" href="learn.php">Read the guide first</a>
    </div>
  </div>
</section>
<?php site_foot(); ?>

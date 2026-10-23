<?php
require_once __DIR__ . '/site_common.php';
$c = site_cfg();
$coin = site_h($c['coin']); $tick = site_h($c['ticker']);
site_head('Learn about ' . $c['coin'] . ' - a beginner\'s guide', 'A plain-language guide to ' . $c['coin'] . ' (' . $c['ticker'] . '): wallets, mining, supply and halving, transactions, the ad network, and staying safe.', 'learn');

// reward schedule straight from the consensus constants: 50 coins, halved every 210,000 blocks
$eras = []; $cum = 0.0;
for ($k = 0; $k < 8; $k++) {
    $reward = 50 / (2 ** $k);
    $cum += $reward * 210000;
    $eras[] = ['era' => $k + 1, 'from' => $k * 210000 + 1, 'to' => ($k + 1) * 210000, 'reward' => $reward, 'cum' => $cum];
}
?>
<div class="page-hero"><div class="wrap">
  <span class="kicker">Beginner's guide</span>
  <h1>How <?= $coin ?> works</h1>
  <p class="lead">Everything you need to understand the coin, in plain language. About ten minutes to read.</p>
</div></div>

<div class="wrap guide">
  <nav class="toc" aria-label="On this page">
    <b>On this page</b>
    <a href="#basics">What is a coin?</a><a href="#different">What's different here</a><a href="#wallet">Wallets &amp; addresses</a>
    <a href="#mining">Mining</a><a href="#supply">Supply &amp; halving</a><a href="#tx">Sending coins</a>
    <a href="#ads">The ad network</a><a href="#safety">Staying safe</a><a href="#glossary">Glossary</a>
  </nav>

  <article class="article">
    <section id="basics">
      <h2>What is a coin?</h2>
      <p>A digital coin is a record of who owns what, kept not by a bank but by thousands of ordinary computers that all check each other's work. The record is called a <strong>blockchain</strong>: a list of <strong>blocks</strong>, each holding a batch of payments and pointing back to the block before it. Change one old payment and every block after it stops matching, so cheating is obvious.</p>
      <p>Who decides the next block? Whoever solves a puzzle first. That is called <strong>proof of work</strong>, and doing it is called <strong>mining</strong>. The winner earns newly created coins plus the fees on the payments in the block. This is how Bitcoin works &mdash; and how <?= $coin ?> works.</p>
    </section>

    <section id="different">
      <h2>What's different about <?= $coin ?></h2>
      <ul>
        <li><strong>It pays for attention.</strong> An advertising network is built into the coin. Advertisers pay <?= $tick ?> per genuine click and publishers earn it, so the coin has a use from day one.</li>
        <li><strong>Fair launch.</strong> The first block creates zero coins. Nobody was given a head start; every coin in existence is mined.</li>
        <li><strong>No accounts.</strong> Your wallet address is your identity. There are no passwords or sign-up forms to leak.</li>
        <li><strong>Its own addresses.</strong> They start with <code>N</code>, so they can't be mistaken for Bitcoin addresses.</li>
        <li><strong>Open source.</strong> The whole program is MIT licensed on <a href="<?= site_h($c['repo']) ?>" rel="noopener">GitHub</a>. Read it, test it, improve it.</li>
      </ul>
      <div class="note warn"><p><strong>Honest note:</strong> <?= $coin ?> is new, experimental and not independently audited. Coins have no guaranteed value and there is no exchange. Never put in more than you can afford to lose.</p></div>
    </section>

    <section id="wallet">
      <h2>Wallets &amp; addresses</h2>
      <p>Your wallet is a file, <code>wallet.json</code>, created by the setup wizard. It contains:</p>
      <ul>
        <li>a <strong>private key</strong> &mdash; a long secret number that proves you own your coins and signs your payments. <strong>Never share it.</strong></li>
        <li>a <strong>public key</strong> and an <strong>address</strong> derived from it. The address (like <code>Nbs54o&hellip;</code>) is what you give people so they can pay you. It is safe to share.</li>
      </ul>
      <div class="note warn"><p><strong>Back it up today.</strong> If <code>wallet.json</code> is lost, your coins are lost for good, and there is no &ldquo;forgot password&rdquo; button. Keep a copy on a USB stick or encrypted drive. Anyone who gets the file can spend your coins.</p></div>
    </section>

    <section id="mining">
      <h2>Mining</h2>
      <p>Mining means your computer repeatedly guesses numbers until the block's fingerprint (a <strong>SHA-256 hash</strong>) falls below a target. The target is set so that, across the whole network, one block is found about every <strong>10 minutes</strong>. When yours is the first valid block, every node accepts it and you receive the reward.</p>
      <ul>
        <li><strong>Difficulty adjusts itself.</strong> Every 2,016 blocks the network compares how long the last stretch took against ten minutes and makes the puzzle harder or easier (by at most four times in either direction).</li>
        <li><strong>Rewards need to mature.</strong> Mined coins can be spent only after 100 further blocks, so a block that gets replaced never leaves anyone holding coins that vanish.</li>
        <li><strong>To mine:</strong> start the wallet with <code>run.bat</code>, open the mining tab and press start. Leaving it on while the PC is idle is the best way to help.</li>
        <li><strong>Be realistic:</strong> on a small network a home PC can find blocks, but electricity costs real money and the coins have no guaranteed value.</li>
      </ul>
    </section>

    <section id="supply">
      <h2>Supply &amp; halving &mdash; why coins can't be printed</h2>
      <p>At most <strong>21,000,000 <?= $tick ?></strong> will ever exist. This isn't a promise &mdash; it's a rule that every node checks on every block:</p>
      <ol>
        <li>The only way new coins appear is the &ldquo;coinbase&rdquo; payment at the top of each block.</li>
        <li>That payment may not exceed the allowed reward plus the block's fees. A block that pays itself more is rejected by every honest node, so it is simply ignored.</li>
        <li>The allowed reward starts at <strong>50 <?= $tick ?></strong> and is <strong>halved every 210,000 blocks</strong> (roughly every four years), and is also capped so the total can never pass 21,000,000.</li>
        <li>Every other payment must spend coins that already exist, and can't create more than it spends.</li>
      </ol>
      <p>Installing the program does not create coins. Everyone starts from the same first block, so everyone shares one chain.</p>
      <div class="tbl-wrap"><table>
        <thead><tr><th>Era</th><th>Blocks</th><th class="num-r">Reward per block</th><th class="num-r">Total ever issued</th></tr></thead>
        <tbody>
        <?php foreach ($eras as $e): ?>
          <tr><td><?= (int)$e['era'] ?></td><td><?= number_format($e['from']) ?> &ndash; <?= number_format($e['to']) ?></td><td class="num-r"><?= rtrim(rtrim(number_format($e['reward'], 4), '0'), '.') ?></td><td class="num-r"><?= number_format($e['cum']) ?></td></tr>
        <?php endforeach; ?>
          <tr><td>&hellip;</td><td>and so on</td><td class="num-r">halves each era</td><td class="num-r">approaches 21,000,000</td></tr>
        </tbody></table></div>
    </section>

    <section id="tx">
      <h2>Sending &amp; receiving</h2>
      <ul>
        <li><strong>Receiving:</strong> give someone your address. Nothing else is needed.</li>
        <li><strong>Sending:</strong> enter their address and an amount in the wallet app. It signs the payment with your private key and sends it to the network.</li>
        <li><strong>Confirmations:</strong> a payment is &ldquo;confirmed&rdquo; once it is in a block, and gets safer with every block added after it. For anything valuable, wait for about six.</li>
        <li><strong>Fees:</strong> a small fee (at least 0.00001 <?= $tick ?>) goes to the miner who includes your payment.</li>
        <li><strong>No chargebacks:</strong> payments can't be reversed. Check the address before you send.</li>
      </ul>
    </section>

    <section id="ads">
      <h2>The ad network</h2>
      <h3>For publishers (website owners)</h3>
      <ol>
        <li>Sign in to the <a href="dashboard8.php">dashboard</a> with your wallet address.</li>
        <li>Create an ad zone and copy the snippet of code it gives you into your web page.</li>
        <li>Ads appear, labelled &ldquo;Ad&rdquo;. Each genuine click earns the ad's price in <?= $tick ?>. Only <strong>one click per page load</strong> is paid, and clicks on your own ads don't count.</li>
        <li>Clicks are held for <strong>24 hours</strong> to filter out bots and fraud, then paid to your wallet.</li>
      </ol>
      <h3>For advertisers</h3>
      <ol>
        <li>Read and accept the <a href="advertiser_terms.php">Advertiser Agreement</a> with your wallet address.</li>
        <li>Pay the one-time <strong>upload fee</strong> (in Bitcoin, through the operator's shop) for each ad you submit. It covers hosting and review.</li>
        <li>Send your ad from the wallet app. It is signed with your key, so nobody can submit ads in your name.</li>
        <li>A person reviews it. Nothing is shown before approval.</li>
        <li>Fund your balance by sending <?= $tick ?> to the network wallet. It counts after 6 confirmations. Each click is then charged at cost until the balance, daily budget or click limit runs out.</li>
      </ol>
      <div class="note"><p>Every ad runs inside a sandbox on the publisher's page, so it can't read the page or run scripts on it. Changing an approved ad sends it back to review.</p></div>
    </section>

    <section id="safety">
      <h2>Staying safe</h2>
      <ul>
        <li>Back up <code>wallet.json</code> and keep it private. Never paste your private key into a website or send it to anyone, including anyone claiming to be &ldquo;support&rdquo;.</li>
        <li>Download <?= $coin ?> only from the <a href="<?= site_h($c['repo']) ?>" rel="noopener">official GitHub repository</a>.</li>
        <li>Start small while the network is young.</li>
        <li>If you run a public node or website, keep Windows, XAMPP and your passwords up to date, and never expose your database to the internet.</li>
        <li>Be wary of anyone promising profits. Nobody can promise what a coin will be worth.</li>
      </ul>
    </section>

    <section id="glossary">
      <h2>Glossary</h2>
      <dl class="gloss">
        <dt>Address</dt><dd>The public identifier, starting with N, that others pay to.</dd>
        <dt>Block</dt><dd>A batch of payments plus a proof-of-work puzzle solution, linked to the previous block.</dd>
        <dt>Blockchain</dt><dd>The shared, ordered list of all blocks.</dd>
        <dt>Coinbase</dt><dd>The special first payment in a block that creates the miner's reward.</dd>
        <dt>Confirmation</dt><dd>Each block added after your payment's block. More is safer.</dd>
        <dt>Difficulty</dt><dd>How hard the mining puzzle currently is. Adjusts every 2,016 blocks.</dd>
        <dt>Halving</dt><dd>The block reward cutting in half every 210,000 blocks.</dd>
        <dt>Hash</dt><dd>A fixed-length fingerprint of data. Change the data and the fingerprint changes completely.</dd>
        <dt>Node</dt><dd>A computer running the program, checking blocks and sharing them with peers.</dd>
        <dt>Private key</dt><dd>The secret that controls your coins. Never share it.</dd>
        <dt>Proof of work</dt><dd>Evidence that real computing effort was spent to make a block.</dd>
        <dt>Publisher / Advertiser</dt><dd>Someone who shows ads / someone who pays to have ads shown.</dd>
      </dl>
    </section>

    <p><a class="btn btn-primary" href="index.php#install">Ready? Install <?= $coin ?></a></p>
  </article>
</div>
<?php site_foot(); ?>

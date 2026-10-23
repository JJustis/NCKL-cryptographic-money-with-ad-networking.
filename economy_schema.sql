-- Advertiser accounts: who has paid in, what has been charged, what is left. Amounts are whole base units (1 coin = 100,000,000).
CREATE TABLE IF NOT EXISTS advertiser_accounts (
  address        VARCHAR(64) NOT NULL PRIMARY KEY,
  balance_sat    BIGINT NOT NULL DEFAULT 0,
  deposited_sat  BIGINT NOT NULL DEFAULT 0,
  spent_sat      BIGINT NOT NULL DEFAULT 0,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- One row per on-chain payment that was credited (the transaction id makes crediting idempotent)
CREATE TABLE IF NOT EXISTS advertiser_deposits (
  tx_id        VARCHAR(100) NOT NULL PRIMARY KEY,
  address      VARCHAR(64) NOT NULL,
  amount_sat   BIGINT NOT NULL,
  block_height INT NOT NULL,
  credited_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_address (address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Statement for each advertiser: deposits (+) and click charges (-)
CREATE TABLE IF NOT EXISTS advertiser_ledger (
  id          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  address     VARCHAR(64) NOT NULL,
  kind        ENUM('deposit','click','refund','adjust') NOT NULL,
  amount_sat  BIGINT NOT NULL,
  ref         VARCHAR(100) NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_address_time (address, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Nothing is served or paid for until a person has approved the ad. New ads appear here as 'pending'.
CREATE TABLE IF NOT EXISTS ad_approvals (
  ad_id       VARCHAR(100) NOT NULL PRIMARY KEY,
  status      ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  note        VARCHAR(255) NULL,
  first_seen  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

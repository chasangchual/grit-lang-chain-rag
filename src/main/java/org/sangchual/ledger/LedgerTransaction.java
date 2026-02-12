package org.sangchual.ledger;

import java.math.BigDecimal;

public class LedgerTransaction {
    private final TransactionType type;
    private final BigDecimal amount;
    private final int timestamp;

    public LedgerTransaction(final TransactionType type, final BigDecimal amount, final
                  int timestamp) {
        this.type = type;
        this.amount = amount;
        this.timestamp = timestamp;
    }

    public TransactionType getType() {
        return type;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public int getTimestamp() {
        return timestamp;
    }
}

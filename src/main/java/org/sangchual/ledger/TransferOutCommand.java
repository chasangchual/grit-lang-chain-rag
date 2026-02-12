package org.sangchual.ledger;

import java.math.BigDecimal;

public class TransferOutCommand extends Command{
    private final User user;
    private final BigDecimal amount;
    public TransferOutCommand(final User user,
                             final BigDecimal amount,
                             final int timestamp) {
        super(timestamp);
        this.user = user;
        this.amount = amount;
    }

    public User getUser() {
        return user;
    }

    public BigDecimal getAmount() {
        return amount;
    }
}

package org.sangchual.ledger;

import java.math.BigDecimal;

public record UserAccount(int userId, BigDecimal balance, int latestTimeStamp) {
    public String toString() {
        return String.format("%s %s %s", String.valueOf(userId), balance.toString(), String.valueOf(latestTimeStamp));
    }
}

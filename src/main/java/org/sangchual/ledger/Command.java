package org.sangchual.ledger;

public class Command {
    private final int timestamp;

    public Command(final int timestamp) {
        this.timestamp = timestamp;
    }

    public int getTimestamp() {
        return timestamp;
    }
}

package org.sangchual.ledger;

public class User {
    private final int id;
    private final String userName;

    public User(final int id, final String userName) {
        this.id = id;
        this.userName = userName;
    }

    public int getId() {
        return id;
    }

    public String getUserName() {
        return userName;
    }
}

package org.sangchual.ledger;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public final class UserRepository {
    private static UserRepository repository = null;
    final Map<String, User> userAccounts = new HashMap<>();

    private UserRepository() {

    }

    public static synchronized UserRepository getInstance() {
        if(repository == null) {
            repository = new UserRepository();
        }
        return repository;
    }

    public boolean add(final String userName) {
        if(userAccounts.containsKey(userName)) {
            return false;
        }
        userAccounts.put(userName, new User(userAccounts.size() + 1, userName));
        return true;
    }

    public Optional<User> find(final String userName) {
        return userAccounts.containsKey(userName) ? Optional.of(userAccounts.get(userName)) : Optional.empty();
    }
}

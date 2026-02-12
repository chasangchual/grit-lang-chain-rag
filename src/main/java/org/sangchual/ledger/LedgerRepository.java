package org.sangchual.ledger;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

import static java.util.Arrays.stream;

public class LedgerRepository {
    private final static Comparator<UserAccount> BY_BALANCE =
            Comparator.comparing(UserAccount::balance);

    private final static Comparator<UserAccount> BY_TIMESTAMP =
            Comparator.comparing(UserAccount::latestTimeStamp);

    private final static Comparator<UserAccount> BY_BALANCE_THEN_TIME =
            Comparator.comparing(UserAccount::balance, Comparator.reverseOrder())
                    .thenComparing(UserAccount::latestTimeStamp);

    private static LedgerRepository instance = null;

    final PriorityQueue<UserLedger> userLedgers;

    private LedgerRepository() {
        userLedgers = new PriorityQueue<>(Comparator.comparingInt(userLeger ->
                userLeger.ledgerTransaction().getTimestamp()));
    }

    public static synchronized LedgerRepository getInstance() {
        if (instance == null) {
            instance = new LedgerRepository();
        }
        return instance;
    }

    public synchronized boolean process(Command command) {
        if (command instanceof DepositCommand depositCommand) {
            processDeposit(depositCommand.getUser(), depositCommand.getAmount(), depositCommand.getTimestamp());
        } else if (command instanceof WithdrawalCommand withdrawalCommand) {
            processWithdrawal(withdrawalCommand.getUser(), withdrawalCommand.getAmount(), withdrawalCommand.getTimestamp());
        } else if (command instanceof TransferOutCommand transferOutCommand) {
            processTransferOut(transferOutCommand.getUser(), transferOutCommand.getAmount(), transferOutCommand.getTimestamp());
        } else {
            throw new IllegalArgumentException("unsupported command type");
        }
        return true;
    }

    private void processDeposit(User user, BigDecimal amount, int timestamp) {
        userLedgers.add(new UserLedger(user.getId(), new LedgerTransaction(TransactionType.DEPOSIT, amount, timestamp)));
    }

    private void processWithdrawal(User user, BigDecimal amount, int timestamp) {
        userLedgers.add(new UserLedger(user.getId(), new LedgerTransaction(TransactionType.WITHDRAWAL, amount, timestamp)));
    }

    private void processTransferOut(User user, BigDecimal amount, int timestamp) {
        userLedgers.add(new UserLedger(user.getId(), new LedgerTransaction(TransactionType.TRANSFER_OUT, amount, timestamp)));
    }

    public BigDecimal getBalance(User user) {
        List<LedgerTransaction> ledgerTransactions = userLedgers.stream().filter(ledger -> ledger.userId() == user.getId()).map(UserLedger::ledgerTransaction).toList();
        BigDecimal balance = BigDecimal.ZERO;

        for (LedgerTransaction ledgerTransaction : ledgerTransactions) {
            if (TransactionType.DEPOSIT == ledgerTransaction.getType()) {
                balance = balance.add(ledgerTransaction.getAmount());
            } else if (TransactionType.WITHDRAWAL == ledgerTransaction.getType()) {
                balance = balance.subtract(ledgerTransaction.getAmount());
            }
        }
        return balance;
    }

    public List<UserAccount> findAll() {
        List<UserAccount> userAccounts = new ArrayList<>();

        Map<Integer, List<UserLedger>> ledgerByUser = userLedgers.stream().collect(Collectors.groupingBy(UserLedger::userId));
        for(Map.Entry<Integer, List<UserLedger>> entry : ledgerByUser.entrySet()) {
            Pair<BigDecimal, Integer> summary = summerize(entry.getValue());
            userAccounts.add(new UserAccount(entry.getKey(), summary.first(), summary.second()));
        }
        return userAccounts.stream().sorted(BY_BALANCE_THEN_TIME).toList();
    }

    public Pair<BigDecimal, Integer> summerize(final List<UserLedger> transactions) {
        BigDecimal balance = BigDecimal.ZERO;
        int latest = -1;

        for (UserLedger ledger : transactions) {
            if (TransactionType.DEPOSIT == ledger.ledgerTransaction().getType()) {
                balance = balance.add(ledger.ledgerTransaction().getAmount());
            } else if (TransactionType.WITHDRAWAL == ledger.ledgerTransaction().getType()) {
                balance = balance.subtract(ledger.ledgerTransaction().getAmount());
            }
            if (ledger.ledgerTransaction().getTimestamp() > latest) {
                latest = ledger.ledgerTransaction().getTimestamp();
            }
        }
        return new Pair<BigDecimal, Integer>(balance, latest);
    }
}

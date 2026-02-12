package org.sangchual;

import org.sangchual.ledger.DepositCommand;
import org.sangchual.ledger.LedgerRepository;
import org.sangchual.ledger.UserRepository;
import org.sangchual.ledger.WithdrawalCommand;

import java.math.BigDecimal;
import java.util.concurrent.atomic.AtomicInteger;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        AtomicInteger timeStamp = new AtomicInteger(0);

        LedgerRepository ledgerRepository = LedgerRepository.getInstance();
        UserRepository userRepository = UserRepository.getInstance();

        userRepository.add("user1");
        userRepository.add("user2");
        userRepository.add("user3");

        ledgerRepository.process(new DepositCommand(userRepository.find("user1").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user1").orElseThrow(), BigDecimal.valueOf(50), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user1").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));

        ledgerRepository.process(new DepositCommand(userRepository.find("user2").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user2").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user2").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user2").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));

        ledgerRepository.process(new DepositCommand(userRepository.find("user3").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user3").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));

        ledgerRepository.process(new WithdrawalCommand(userRepository.find("user1").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));
        ledgerRepository.process(new WithdrawalCommand(userRepository.find("user1").orElseThrow(), BigDecimal.valueOf(30), timeStamp.getAndIncrement()));

        ledgerRepository.process(new WithdrawalCommand(userRepository.find("user2").orElseThrow(), BigDecimal.valueOf(15), timeStamp.getAndIncrement()));

        System.out.println(ledgerRepository.getBalance(userRepository.find("user1").orElseThrow()));
        System.out.println(ledgerRepository.getBalance(userRepository.find("user2").orElseThrow()));
        System.out.println(ledgerRepository.getBalance(userRepository.find("user3").orElseThrow()));

        userRepository.add("user4");
        ledgerRepository.process(new DepositCommand(userRepository.find("user4").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));
        ledgerRepository.process(new DepositCommand(userRepository.find("user4").orElseThrow(), BigDecimal.valueOf(100), timeStamp.getAndIncrement()));

        System.out.println(ledgerRepository.getBalance(userRepository.find("user4").orElseThrow()));

        ledgerRepository.findAll().forEach(userAccount -> System.out.println(userAccount.toString()));
    }
}
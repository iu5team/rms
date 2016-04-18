package models;

import java.util.*;

/**
 * 
 */
public class Employee {

    /**
     * Default constructor
     */
    public Employee() {
    }

    /**
     * 
     */
    public Employee manager;

    /**
     * 
     */
    public Employee[] subordinates;

    /**
     * 
     */
    public Position position;

    /**
     * 
     */
    public String name;






    /**
     * 
     */
    public void changeInformation() {
        // TODO implement here
    }

    /**
     * 
     */
    public void delete() {
        // TODO implement here
    }

    /**
     * 
     */
    public void setVacation() {
        // TODO implement here
    }

    /**
     * 
     */
    public void setSickDay() {
        // TODO implement here
    }

    /**
     * 
     */
    public void setManager() {
        // TODO implement here
    }

    /**
     * 
     */
    public void setPostion(Position position) {
        this.position = position;
    }

    /**
     * 
     */
    public void setSalary() {
        // TODO implement here
    }

}
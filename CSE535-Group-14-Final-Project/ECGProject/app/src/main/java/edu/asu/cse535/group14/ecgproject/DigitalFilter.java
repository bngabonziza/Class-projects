package edu.asu.cse535.group14.ecgproject;

public interface DigitalFilter {

    public abstract double filter(double sample);

    public abstract double[] filter(double[] sample);

    public abstract void resetFilter();
}
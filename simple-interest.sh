#!/bin/bash


# Simple Interest Calculator


# Function to calculate simple interest

calculate_simple_interest() {

    principal=$1

    rate=$2

    time=$3


    # Formula for simple interest: I = P * R * T / 100

    interest=$(echo "scale=2; $principal * $rate * $time / 100" | bc)

    echo "Simple Interest: $interest"

}


# Input principal amount

read -p "Enter Principal Amount: " principal


# Input annual interest rate

read -p "Enter Annual Interest Rate (%): " rate


# Input time (in years)

read -p "Enter Time (in Years): " time


# Validate inputs

if [ -z "$principal" ] || [ -z "$rate" ] || [ -z "$time" ]; then

    echo "Please enter valid input for Principal, Rate, and Time."

    exit 1

fi


# Calculate and display simple interest

calculate_simple_interest $principal $rate $time


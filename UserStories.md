# KC Scenario - BlueWater Phase

Once the ship departs port, there are a series of user stories around understanding and managing container health while in transit.

**Key Role:**
**_Shipping Agent:_**

1. As a Shipping Agent, I’d like to efficiently understand the health of and manage the operations of reefer containers in transit, to ensure that I am effectively protecting goods in my care, and managing cost
    * As a Shipping Agent, I need to understand when  a container isn’t operating within normal boundaries and automatically take corrective action
        * As a Shipping Agent, I’d like to understand when a container temperatures are trending towards a boundary and may need a reset
        * As a Shipping Agent, I’d like to understand when containers may have a potential failure so I can proactively take action to protect goods in transit
        * As a Shipping Agent, I’d like to understand when a container is failing so I can take corrective action
        * As a Shipping Agent, I’d like to automatically manage container settings based on any course or route deviations or rerouting events

## Policies

1. Temp is rising && no power consumption  ==> reset power and thermostat
2. Temp is rising && power consumption is flat ==> Potential Failure -> reset & notify
3. Temp is rising and power is rising ==> Failing -> notify
4. Temp is dropping below bounds ==> reset thermostat

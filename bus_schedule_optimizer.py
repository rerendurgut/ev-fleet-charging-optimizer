from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value
import pandas as pd
import numpy as np

class BusScheduleOptimizer:
    def __init__(self):
        # Parameters that will be set manually
        self.bus_capacity = 0  # kWh
        self.min_charge_threshold = 0  # kWh
        self.station_charging_capacity = []  # List of charging capacity by time
        self.depot_distance_energy = 0  # kWh needed to reach depot
        self.idle_cost_per_minute = 0
        self.num_buses = 0
        
    def load_data(self, schedule_file, charging_capacity_file):
        self.schedule_df = pd.read_csv(schedule_file)
        # Fix for single-column CSVs with semicolon-separated values
        if len(self.schedule_df.columns) == 1 and ';' in self.schedule_df.columns[0]:
            self.schedule_df = pd.read_csv(schedule_file, sep=';')
            self.schedule_df.columns = [col.strip().lower().replace(" ", "_") for col in self.schedule_df.columns]
        else:
            self.schedule_df.columns = [col.strip().lower().replace(" ", "_") for col in self.schedule_df.columns]
        # Try to find the line column more robustly
        possible_line_cols = ['line', 'code', 'line_id', 'line_']
        found = False
        for col in possible_line_cols:
            if col in self.schedule_df.columns:
                if col != 'line':
                    self.schedule_df = self.schedule_df.rename(columns={col: 'line'})
                found = True
                break
        if not found:
            raise KeyError(f"No column found for bus line. Found columns: {self.schedule_df.columns.tolist()}")
        # Load time-dependent charging capacity
        self.charging_df = pd.read_csv(charging_capacity_file)
        # Standardize charging_df columns
        self.charging_df.columns = [col.strip().lower().replace(" ", "_") for col in self.charging_df.columns]
        # Fix for European decimal and missing 'charging_rate'
        if 'charging_rate' not in self.charging_df.columns:
            last_col = self.charging_df.columns[-1]
            self.charging_df['charging_rate'] = (
                self.charging_df[last_col]
                .astype(str)
                .str.replace(',', '.')
                .replace('', '0')
                .astype(float)
                .fillna(0)
            )
        else:
            self.charging_df['charging_rate'] = (
                self.charging_df['charging_rate']
                .astype(str)
                .str.replace(',', '.')
                .replace('', '0')
                .astype(float)
                .fillna(0)
            )
        # Ensure 'station_capacity' exists and is numeric, default to number of buses if missing
        if 'station_capacity' not in self.charging_df.columns:
            self.charging_df['station_capacity'] = self.num_buses
        else:
            self.charging_df['station_capacity'] = (
                self.charging_df['station_capacity']
                .replace('', self.num_buses)
                .fillna(self.num_buses)
                .astype(float)
            )
        # If 'time' column does not exist, create it as a string version of the index
        if 'time' not in self.charging_df.columns:
            self.charging_df['time'] = self.charging_df.index.astype(str)
        if 'energy_cost' not in self.schedule_df.columns:
            self.schedule_df['energy_cost'] = 10  # or compute based on depart/arrive
        
    def set_parameters(self, bus_capacity, min_charge_threshold, 
                      depot_distance_energy, idle_cost_per_minute, num_buses):
        self.bus_capacity = bus_capacity
        self.min_charge_threshold = min_charge_threshold
        self.depot_distance_energy = depot_distance_energy
        self.idle_cost_per_minute = idle_cost_per_minute
        self.num_buses = num_buses
        
    def solve(self):
        # Create the model
        prob = LpProblem("Electric_Bus_Scheduling", LpMinimize)
        
        # Time periods
        time_periods = range(len(self.charging_df))
        # Use lower-case column names
        lines = self.schedule_df['line'].unique()
        buses = range(self.num_buses)
        
        # Decision Variables
        x = LpVariable.dicts("bus_line",
                            ((b, t, l) for b in buses 
                             for t in time_periods 
                             for l in lines),
                            cat='Binary')
        
        charging = LpVariable.dicts("charging",
                                  ((b, t) for b in buses 
                                   for t in time_periods),
                                  cat='Binary')
        
        battery_level = LpVariable.dicts("battery",
                                       ((b, t) for b in buses 
                                        for t in time_periods),
                                       lowBound=0,
                                       upBound=self.bus_capacity)
        
        # Objective Function
        prob += (
            lpSum([
                self.schedule_df[
                    (self.schedule_df['line'] == l) & 
                    (self.schedule_df['depart'] == str(t))
                ]['energy_cost'].iloc[0] * x[b, t, l]
                for b in buses for t in time_periods for l in lines
                if not self.schedule_df[
                    (self.schedule_df['line'] == l) & 
                    (self.schedule_df['depart'] == str(t))
                ].empty
            ]) +
            lpSum([
                self.idle_cost_per_minute * (1 - charging[b, t] - lpSum(x[b, t, l] for l in lines))
                for b in buses for t in time_periods
            ])
        )
        
        # Constraints
        # Battery initialization at t=0
        for b in buses:
            prob += battery_level[b, 0] == self.bus_capacity

        # Battery dynamics
        for b in buses:
            for t in time_periods[1:]:
                # Ensure charging_rate is a valid float (no NaN/inf)
                charging_rate = float(self.charging_df['charging_rate'].iloc[t]) if pd.notnull(self.charging_df['charging_rate'].iloc[t]) else 0.0
                prob += (
                    battery_level[b, t] ==
                    battery_level[b, t-1]
                    - lpSum([
                        self.schedule_df[
                            (self.schedule_df['line'] == l) & 
                            (self.schedule_df['depart'] == str(t))
                        ]['energy_cost'].iloc[0] * x[b, t, l]
                        for l in lines
                        if not self.schedule_df[
                            (self.schedule_df['line'] == l) & 
                            (self.schedule_df['depart'] == str(t))
                        ].empty
                    ])
                    + (charging_rate * self.bus_capacity) * charging[b, t]
                )
        
        # Minimum battery level
        for b in buses:
            for t in time_periods:
                prob += battery_level[b, t] >= self.min_charge_threshold
        
        # Charging station capacity
        for t in time_periods:
            prob += (lpSum(charging[b, t] for b in buses) <= 
                    float(self.charging_df['station_capacity'].iloc[t]))
        
        # Bus can only do one thing at a time
        for b in buses:
            for t in time_periods:
                prob += (charging[b, t] + 
                        lpSum(x[b, t, l] for l in lines) <= 1)
        
        # Solve the problem with explicit CBC solver for reproducibility
        from pulp import PULP_CBC_CMD
        prob.solve(PULP_CBC_CMD())
        
        return {
            'status': LpStatus[prob.status],
            'schedule': self.extract_schedule(x, charging, battery_level, buses, time_periods, lines)
        }

    def extract_schedule(self, x, charging, battery_level, buses, time_periods, lines):
        """
        Convert the optimization solution to a readable schedule format.
        """
        schedule = []
        for b in buses:
            for t in time_periods:
                action = 'idle'
                line_assigned = None
                for l in lines:
                    if x[b, t, l].varValue is not None and x[b, t, l].varValue > 0.5:
                        action = 'line'
                        line_assigned = l
                        break
                if charging[b, t].varValue is not None and charging[b, t].varValue > 0.5:
                    action = 'charging'
                schedule.append({
                    'bus': b,
                    'time': t,
                    'action': action,
                    'line': line_assigned,
                    'battery': battery_level[b, t].varValue if battery_level[b, t].varValue is not None else None
                })
        return schedule

# Usage example:
if __name__ == "__main__":
    optimizer = BusScheduleOptimizer()
    optimizer.load_data("/Users/receperendurgut/Desktop/BME/Electromobility/schedule.csv", "/Users/receperendurgut/Desktop/BME/Electromobility/charging_capacity.csv")
    optimizer.set_parameters(
         bus_capacity=300,  # kWh
         min_charge_threshold=50,  # kWh
         depot_distance_energy=20,  # kWh
         idle_cost_per_minute=0.1,  # cost units
         num_buses=20
     )
    result = optimizer.solve()
    print(result)

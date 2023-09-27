import sys
import pandas as pd
import time, numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

#Parameters
T = 6 # Planning Horizon

Io = 0 # Initial Inventory Level

In = 0 # Final Inventory Level

d = np.array([60,100,140,200,120,80]) # d_t

K = np.array([180,140,160,160,170,190]) # K_t

c = np.array([7,7,8,7,6,10]) # c_t

h = np.array([1,1,2,2,2,2]) # h_t

C = np.array([10000,10000,10000,10000,10000,10000]) # C_t

range_t = range(1,T+1) # Time t=0 not taken into account

#Create Model
model = pyo.ConcreteModel()

#Define variables                           ### Do note that Variables' have T+1 element
                                            ### and parameters array have T elements therefore constraints are arranged accordingly in terms of indexing
model.I = pyo.Var(range(0,T+1), # index t
                  bounds = (0,None))

model.y = pyo.Var(range(0,T+1), # index t
                  within=Binary)

model.q = pyo.Var(range(0,T+1), # index t
                  bounds = (0,None))

I = model.I
y = model.y
q = model.q

#Constraints 

model.C1 = pyo.Constraint(expr= I[0] == Io ) # Set Io

model.C2 = pyo.Constraint(expr= I[T] == In ) # Set In

model.C3 = pyo.ConstraintList() 
for t in range_t:
    model.C3.add(expr= q[t] + I[t-1] - I[t] == d[t-1])
    
model.C4 = pyo.ConstraintList() 
for t in range_t:
    model.C4.add(expr= q[t] -C[t-1]*y[t] <= 0)
    

# Define Objective Function
model.obj = pyo.Objective(expr = sum(K[t-1]*y[t] +c[t-1]*q[t]+h[t-1]*I[t] for t in range_t), 
                          sense = minimize)
    
begin = time.time()
opt = SolverFactory('cplex')
results = opt.solve(model)

deltaT = time.time() - begin # Compute Exection Duration

model.pprint()

sys.stdout = open("Capacitated_Lot_Sizing_Problem_CLSP_Problem_Results.txt", "w") #Print Results on a .txt file

print('Time =', np.round(deltaT,2))

if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):

    print('Total Cost (Obj value) =', pyo.value(model.obj))
    print('Solver Status is =', results.solver.status)
    print('Termination Condition is =', results.solver.termination_condition)
    print(" " )
    
    for t in range_t:
        print("Time t = ", t )
        print("---> q[", t ,"] = ",pyo.value(q[t]))
        print("---> I[", t ,"] = ",pyo.value(I[t]))
        print("---> y[", t ,"] = ",pyo.value(y[t]))
elif (results.solver.termination_condition == TerminationCondition.infeasible):
   print('Model is unfeasible')
  #print('Solver Status is =', results.solver.status)
   print('Termination Condition is =', results.solver.termination_condition)
else:
    # Something else is wrong
    print ('Solver Status: ',  result.solver.status)
    print('Termination Condition is =', results.solver.termination_condition)
    
sys.stdout.close()
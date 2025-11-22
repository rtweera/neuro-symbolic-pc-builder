% --- knowledge_base.pl ---

% FACTS: Hardware specs
% ======================================
% syntax: cpu(Model, Socket, Price, CoreCount).
cpu(i9_14900k, lga1700, 580, 24).
cpu(i5_13600k, lga1700, 300, 14).
cpu(ryzen_7800x3d, am5, 450, 8).

% syntax: motherboard(Model, Socket, Price).
motherboard(z790_aorus, lga1700, 250).
motherboard(b650_tomahawk, am5, 200).

% RULES: Logic for compatibility
% ======================================
% A CPU and Mobo are compatible if they share the same Socket.
compatible_build(CpuModel, MoboModel, TotalCost) :-
    cpu(CpuModel, Socket, CpuPrice, _),
    motherboard(MoboModel, Socket, MoboPrice),
    TotalCost is CpuPrice + MoboPrice.

% QUERY HELPERS: Find builds under a budget
% ======================================
recommend_build(MaxBudget, Cpu, Mobo, Cost) :-
    compatible_build(Cpu, Mobo, Cost),
    Cost =< MaxBudget.
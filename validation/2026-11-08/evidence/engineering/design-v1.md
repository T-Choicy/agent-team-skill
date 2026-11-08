# Architect design v1

Author: /root/trial_physics_lead/architect; selected gpt-6.1-sol / medium.
Lead transcription of the Architect proposal, preserving all acceptance requirements.

## Goal and scope

Standard-library Python velocity Verlet for dimensionless x''=-x, x(0)=1, v(0)=0. Analytic reference x(t)=cos(t), v(t)=-sin(t); continuous energy E=(x*x+v*v)/2=0.5.
Only oscillator.py and test_oscillator.py in C:/Users/Administrator/source/agent-team-skill/validation/2026-11-08/engineering; sole writer /root/trial_physics_lead/implementer. Directory was empty; no callers, fixtures, exports, package configuration or dependencies require changes. No production changes.

## API

solve(dt, steps) returns a list of (t,x,v) tuples.
- dt accepts built-in int or float excluding bool; other types raise TypeError. dt must be finite and 0<dt<2, else ValueError.
- steps accepts built-in int excluding bool; other types raise TypeError. Negative steps raises ValueError.
- Validate both arguments before allocating trajectory or integrating.
- Exactly steps+1 samples including (0.0,1.0,0.0). Sample n has time n*dt. steps=0 returns singleton initial sample.
- No implicit coercion, file I/O, console output, CLI, mutable globals, configurable initial conditions or physical parameters.
- Docstring states equation, initial conditions, argument contract, sample layout and O(steps) time/memory.
- No arbitrary maximum length; huge trajectories and floating-point representability extremes are outside demonstrated operating range. Strings, complex, Decimal and third-party scalar types rejected.

## Physics and algorithm

For old x,v and h=dt:
x_new=x+h*v-0.5*h*h*x
v_new=v-0.5*h*(x+x_new)
Preserve old x until velocity calculation, then update stored state.

Unit frequency dimensionless conservative oscillator, no damping/forcing/coupling/fitted parameters. Bounded oscillatory modes for 0<h<2; h=2 excluded. Stability does not guarantee accuracy. Continuous energy is not exactly conserved. Expected trajectory and bounded energy error are second order in h.
Exact-arithmetic invariant v_n^2+(1-h^2/4)*x_n^2=1-h^2/4 implies 0.5-h^2/8 <= E_n <=0.5 for specified initial state. Floating-point slack required; no arbitrary-duration guarantee.

## Verification contract

All tests in test_oscillator.py using unittest/math/built-ins, conventional unittest.main guard.
1. Exact singleton for zero steps.
2. h=0.1, one step: two samples, exact initial sample and final time 0.1; x=0.995,v=-0.09975 within absolute 1e-14.
3. h=0.1,100 steps: every time equals n*h; maximum absolute position and velocity errors against cos(t),-sin(t) each <0.01.
4. h=0.1,20000 steps: every E between 0.5-h*h/8-1e-10 and 0.5+1e-10. Finite duration T=2000 only.
5. At fixed T=10, (h,steps)=(0.2,50),(0.1,100),(0.05,200). Endpoint error hypot(x-cos(T),v+sin(T)). Positive strictly decreasing errors and each adjacent coarse/fine ratio in [3.5,4.5]. Proposed criteria, not measured results. Failures preserved/investigated before changing thresholds.
6. Invalid inputs via subtests: dt True,string,None,complex -> TypeError; dt 0,negative,2,greater than 2,nan,inf,-inf -> ValueError. steps True,1.0,string,None -> TypeError; negative integer -> ValueError.
7. Accepted integer dt: solve(1,1) yields x=0.5,v=-0.75.

Actual evidence commands from workspace:
python -m unittest -v test_oscillator
python -m py_compile oscillator.py test_oscillator.py
Use evidence.py run for actual argv/cwd/exit/stdout/stderr/source hashes. Compile covers syntax only. Engineering reviewer additionally inspects full sources and independently checks behavior. Physics reviewer independently checks analytic trajectory, energy and order against the same frozen snapshot. Independent delivery review precedes freeze; both exact Design ID reviews precede implementation.

## Alternatives and boundaries

Single function/list-of-tuples recommended; high confidence subject to independent review and execution. Generator complicates validation timing/repeated analysis; classes, energy helper, CLI, configurable physics and dependencies add unnecessary interfaces. Forward Euler has unsuitable energy growth.
O(steps) storage, accumulating phase error and finite precision limit this fixture. No inference about hardware or dimensional research systems. No unresolved physical choice within fixed equation/initial conditions. Design changes require new version/hash and dual design review. Frozen source changes require thaw event, repair, self-test, delivery review, new snapshot and both validations.
Skipped configurable physics, plots, packaging, external references and performance benchmarks. This finite happy-path workflow trial does not verify every failure branch or production physics.

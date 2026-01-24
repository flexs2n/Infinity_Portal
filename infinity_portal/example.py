from infinity_portal import AutonomousStrategySystem

# Initialize
system = AutonomousStrategySystem()

# Run pipeline
result = system.run_full_pipeline(
    ticker="NVDA",
    optimization_target="sharpe"
)

print(f"Best Sharpe: {result['best_sharpe']}")

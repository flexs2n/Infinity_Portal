# infinity_portal/dashboard_generator.py (NEW FILE)

from typing import Dict, List
from datetime import datetime

class TrustDashboard:
    """
    Generates ASCII dashboard for confidence breakdown
    """
    
    @staticmethod
    def generate_trust_bar(score: float, width: int = 20) -> str:
        """Generate progress bar for trust score"""
        filled = int(score * width)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    @staticmethod
    def get_confidence_level(score: float) -> str:
        """Convert score to label"""
        if score >= 0.8:
            return "High"
        elif score >= 0.5:
            return "Medium"
        else:
            return "LOW"
    
    @staticmethod
    def generate_dashboard(
        overall_confidence: float,
        trust_scores: Dict[str, float],
        risk_factors: List[Dict],
        recommendations: List[str],
        divergence_data: Dict = None
    ) -> str:
        """
        Generate complete trust breakdown dashboard
        """
        dashboard = f"""
┌─────────────────────────────────────────────────────────┐
│         DECISION CONFIDENCE BREAKDOWN                    │
├─────────────────────────────────────────────────────────┤
│ Overall Confidence: {overall_confidence:.2f} ({TrustDashboard.get_confidence_level(overall_confidence).upper()})                       │
│                                                          │
│ Data Source Trust:                                      │
"""
        
        # Add trust scores for each feed
        for source, score in trust_scores.items():
            bar = TrustDashboard.generate_trust_bar(score)
            label = TrustDashboard.get_confidence_level(score)
            dashboard += f"│  {bar} {source.capitalize():15s} {score:.2f} ({label})"
            
            # Pad to align
            dashboard += " " * (56 - len(dashboard.split('\n')[-1])) + "│\n"
        
        # Add divergence data if present
        if divergence_data and divergence_data.get('has_divergence'):
            div = divergence_data
            dashboard += f"""│                                                          │
│ Sentiment-Price Divergence:                             │
│  🚨 {div['divergence_type']} divergence detected        │
│     Severity: {div['severity']:8s} | Confidence: {div['confidence']:.2f}    │
"""
        
        # Add active risk factors
        dashboard += f"""│                                                          │
│ Active Risk Factors:                                    │
"""
        if risk_factors:
            for risk in risk_factors:
                icon = "⚠️" if risk['severity'] != 'HIGH' else "🚨"
                dashboard += f"│  {icon} {risk['code']}: {risk['message'][:48]}"
                dashboard += " " * (56 - len(dashboard.split('\n')[-1])) + "│\n"
        else:
            dashboard += "│  ✓ No active risk factors                                │\n"
        
        # Add recommendations
        dashboard += f"""│                                                          │
│ What Would Increase Confidence:                         │
"""
        for rec in recommendations:
            dashboard += f"│  {rec[:56]}"
            dashboard += " " * (58 - len(dashboard.split('\n')[-1])) + "│\n"
        
        dashboard += "└─────────────────────────────────────────────────────────┘"
        
        return dashboard


# Usage example
if __name__ == "__main__":
    dashboard = TrustDashboard.generate_dashboard(
        overall_confidence=0.62,
        trust_scores={
            'binance': 0.85,
            'coinbase': 0.72,
            'kraken': 0.31,
            'finnhub_sentiment': 0.78
        },
        risk_factors=[
            {'code': 'FD04', 'severity': 'MEDIUM', 'message': 'Kraken feed delayed by 12 seconds'},
            {'code': 'FD01', 'severity': 'MEDIUM', 'message': '1.2% price spread across exchanges'},
        ],
        recommendations=[
            "✓ Wait for Kraken feed to update",
            "✓ Price spread narrows to < 0.5%",
            "✓ Trading volume picks up"
        ]
    )
    print(dashboard)
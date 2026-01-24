# infinity_portal/trader_interface.py (NEW FILE)

from typing import Dict, List, Callable
from loguru import logger
import re

class TraderQuestionnaire:
    """
    Interactive system that asks trader questions
    and adjusts confidence based on responses
    """
    
    def __init__(self):
        self.adjustment_history = []
    
    def ask_question(
        self,
        question: str,
        context: Dict,
        response_handler: Callable
    ) -> Dict:
        """
        Ask trader a question and process response
        
        Args:
            question: Question to ask
            context: Context data (prices, risk factors, etc.)
            response_handler: Function to process response
        
        Returns:
            {
                'question': str,
                'trader_response': str,
                'confidence_adjustment': float,
                'explanation': str,
                'updated_recommendation': str
            }
        """
        # In a real system, this would use input() or web form
        # For API integration, this would be an endpoint
        
        logger.info(f"\n🤔 Question for Trader: {question}")
        
        # Simulated response for demonstration
        # In production: trader_response = input("Your answer: ")
        trader_response = "SIMULATED_RESPONSE"
        
        # Process response through handler
        result = response_handler(trader_response, context)
        
        # Log adjustment
        self.adjustment_history.append({
            'question': question,
            'response': trader_response,
            'adjustment': result['confidence_adjustment'],
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def handle_exchange_gap_question(
        self, 
        response: str, 
        context: Dict
    ) -> Dict:
        """
        Handler for exchange price gap questions
        """
        response_lower = response.lower()
        
        # Positive indicators
        if any(word in response_lower for word in ['normal', 'typical', 'expected', 'yes']):
            adjustment = +0.15
            explanation = (
                "Trader confirms gap is within normal range for "
                "current market conditions. Risk severity reduced."
            )
            updated_recommendation = "EXECUTE"
            
        # Negative indicators
        elif any(word in response_lower for word in ['unusual', 'concerning', 'suspicious', 'no']):
            adjustment = -0.20
            explanation = (
                "Trader flags price gap as unusual. "
                "Increasing caution level. Consider waiting."
            )
            updated_recommendation = "WAIT"
            
        # Uncertain
        else:
            adjustment = 0.0
            explanation = "Trader response unclear. No confidence adjustment."
            updated_recommendation = "REVIEW"
        
        return {
            'confidence_adjustment': adjustment,
            'explanation': explanation,
            'updated_recommendation': updated_recommendation
        }
    
    def handle_divergence_question(
        self, 
        response: str, 
        context: Dict
    ) -> Dict:
        """
        Handler for sentiment-price divergence questions
        """
        response_lower = response.lower()
        
        # Check for institutional activity mentions
        if any(word in response_lower for word in ['institution', 'accumulating', 'whale', 'buying']):
            adjustment = +0.10
            explanation = (
                "Trader reports institutional buying activity. "
                "This explains price resilience despite negative sentiment. "
                "Divergence risk reduced."
            )
            context['divergence_severity'] = 'LOW'  # Downgrade
            
        # Check for insider information
        elif any(word in response_lower for word in ['insider', 'selling', 'dumping']):
            adjustment = -0.15
            explanation = (
                "Trader suspects insider selling. "
                "Divergence may signal deeper issues. Increasing caution."
            )
            context['divergence_severity'] = 'HIGH'  # Upgrade
            
        else:
            adjustment = 0.0
            explanation = "No specific information provided about divergence cause."
        
        return {
            'confidence_adjustment': adjustment,
            'explanation': explanation,
            'updated_recommendation': 'EXECUTE' if adjustment > 0 else 'WAIT'
        }
    
    def handle_feed_quality_rating(
        self, 
        response: str, 
        context: Dict
    ) -> Dict:
        """
        Handler for feed quality rating (1-5 scale)
        """
        # Extract number from response
        rating_match = re.search(r'[1-5]', response)
        
        if rating_match:
            rating = int(rating_match.group())
            
            # Convert 1-5 scale to trust score (0.2-1.0)
            new_trust_score = rating / 5.0
            
            # Get exchange name from context
            exchange = context.get('exchange', 'unknown')
            old_trust = context.get('old_trust_score', 0.85)
            
            # Calculate confidence impact
            trust_change = new_trust_score - old_trust
            confidence_adjustment = trust_change * 0.5  # Scale to overall confidence
            
            explanation = (
                f"Trader rates {exchange} feed quality: {rating}/5. "
                f"Trust score adjusted from {old_trust:.2f} to {new_trust_score:.2f}. "
            )
            
            if rating <= 2:
                explanation += "Low rating indicates potential data quality issues."
                updated_recommendation = "WAIT"
            else:
                explanation += "Rating indicates acceptable data quality."
                updated_recommendation = "EXECUTE"
            
            # Update context
            context['trust_scores'][exchange] = new_trust_score
            
            return {
                'confidence_adjustment': confidence_adjustment,
                'explanation': explanation,
                'updated_recommendation': updated_recommendation,
                'new_trust_score': new_trust_score
            }
        
        else:
            return {
                'confidence_adjustment': 0.0,
                'explanation': "Could not parse rating from response.",
                'updated_recommendation': 'REVIEW'
            }
    
    def generate_questions_from_context(
        self, 
        context: Dict
    ) -> List[Dict]:
        """
        Automatically generate relevant questions based on current state
        
        Args:
            context: {
                'risk_factors': List[Dict],
                'divergence': Dict,
                'trust_scores': Dict,
                'confidence': float
            }
        
        Returns:
            List of question objects with handlers
        """
        questions = []
        
        # Question about price spreads
        if any(r['code'] == 'FD01' for r in context.get('risk_factors', [])):
            spread_risk = next(r for r in context['risk_factors'] if r['code'] == 'FD01')
            questions.append({
                'question': (
                    f"Price shows {spread_risk['message']}. "
                    "Have you seen this pattern before for this asset?"
                ),
                'handler': self.handle_exchange_gap_question,
                'priority': 'high'
            })
        
        # Question about divergence
        if context.get('divergence', {}).get('has_divergence'):
            div = context['divergence']
            questions.append({
                'question': (
                    f"News sentiment is {div['divergence_type'].lower()} "
                    f"but price is moving opposite direction. "
                    "Do you have information that might explain this?"
                ),
                'handler': self.handle_divergence_question,
                'priority': 'high'
            })
        
        # Question about low-trust feeds
        for exchange, score in context.get('trust_scores', {}).items():
            if score < 0.5:
                questions.append({
                    'question': (
                        f"Rate your confidence in {exchange}'s data feed "
                        f"today (1-5, where 5 is very confident)"
                    ),
                    'handler': self.handle_feed_quality_rating,
                    'priority': 'medium',
                    'context_data': {
                        'exchange': exchange,
                        'old_trust_score': score
                    }
                })
        
        return sorted(questions, key=lambda x: x['priority'], reverse=True)


# Example integration with infinity_portal
class Interactiveinfinity_portal(infinity_portal):
    """
    Extended infinity_portal with interactive trader input
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questionnaire = TraderQuestionnaire()
        self.interactive_mode = kwargs.get('interactive_mode', False)
    
    def run_with_trader_input(self, task: str, *args, **kwargs):
        """
        Run trading cycle with interactive trader questions
        """
        # Run normal analysis first
        initial_result = self.run(task, *args, **kwargs)
        
        if not self.interactive_mode:
            return initial_result
        
        # Build context for questions
        context = {
            'risk_factors': self.risk_factors,  # From analysis
            'divergence': self.divergence_data,  # From divergence detector
            'trust_scores': self.exchange_monitor.trust_scores,
            'confidence': self.overall_confidence
        }
        
        # Generate and ask questions
        questions = self.questionnaire.generate_questions_from_context(context)
        
        for q in questions:
            result = self.questionnaire.ask_question(
                question=q['question'],
                context={**context, **q.get('context_data', {})},
                response_handler=q['handler']
            )
            
            # Adjust confidence
            self.overall_confidence += result['confidence_adjustment']
            self.overall_confidence = max(0.0, min(1.0, self.overall_confidence))
            
            logger.info(f"📊 Confidence adjusted to: {self.overall_confidence:.2f}")
            logger.info(f"💡 {result['explanation']}")
        
        return {
            'initial_analysis': initial_result,
            'trader_adjustments': self.questionnaire.adjustment_history,
            'final_confidence': self.overall_confidence
        }
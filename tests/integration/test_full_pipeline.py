"""
Integration Tests for Full Autonomous Pipeline
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infinity_portal.autonomous_strategy_system import AutonomousStrategySystem


@pytest.mark.integration
class TestFullPipeline:
    """Integration tests for complete workflow"""
    
    @pytest.mark.slow
    def test_data_collection(self):
        """Test that data collection works"""
        system = AutonomousStrategySystem()
        
        data = system.collect_data("AAPL")
        
        assert 'social_data' in data
        assert 'news_data' in data
        assert 'price_data' in data
    
    @pytest.mark.slow
    def test_edge_discovery(self, sample_social_data, sample_news_data):
        """Test edge discovery with sample data"""
        system = AutonomousStrategySystem()
        
        data = {
            'social_data': sample_social_data,
            'news_data': sample_news_data,
            'price_data': {'current_price': 150, 'change_percent': 2.5}
        }
        
        edges = system.discover_edges("TEST", data)
        
        assert 'edges_discovered' in edges
        assert isinstance(edges['edges_discovered'], list)



if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
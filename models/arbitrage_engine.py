#!/usr/bin/env python3
"""
Module 4: Moteur d'Arbitrage (Heuristique + Filtre de Marge & Ratio de Vélocité)
Formule de Marge Nette :
Marge Nette = Prix marché projeté - (Prix achat + Port + Frais eBay ~13% + Marge cible)
Score de Vélocité = Ratio (Sold listings / Active listings)
"""

class ArbitrageEngine:
    def __init__(self, ebay_fee_pct=0.1325, target_margin_min_pct=0.15):
        self.ebay_fee_pct = ebay_fee_pct
        self.target_margin_min_pct = target_margin_min_pct

    def calculate_arbitrage_metrics(self, listing_price, predicted_market_price, shipping_fee=4.99, sold_count=18, active_count=5):
        """
        Calcule la Marge Nette exacte après déduction de tous les frais :
        - Frais de vente commission eBay (~13.25%)
        - Frais de livraison & port
        - Ratio de vélocité de vente (Ventes passées / Annonces actives)
        """
        ebay_fees = round(predicted_market_price * self.ebay_fee_pct, 2)
        total_costs = round(listing_price + shipping_fee + ebay_fees, 2)
        
        # Marge Nette Brute ($)
        net_margin_dollar = round(predicted_market_price - total_costs, 2)
        
        # Rendement ROI (%) Net
        profit_margin_pct = round((net_margin_dollar / (listing_price + shipping_fee)) * 100.0, 2) if (listing_price + shipping_fee) > 0 else 0.0

        # Score de Vélocité = Ratio (Sold Listings / Active Listings)
        if active_count > 0:
            sales_velocity_ratio = round(sold_count / float(active_count), 2)
        else:
            sales_velocity_ratio = 1.0

        # Statut d'Opportunité
        is_viable_opportunity = net_margin_dollar >= 20.0 and profit_margin_pct >= (self.target_margin_min_pct * 100.0)

        return {
            "ebay_fees": ebay_fees,
            "total_costs": total_costs,
            "arbitrage_score": net_margin_dollar, # Gain Net ($)
            "profit_margin_pct": profit_margin_pct,
            "sales_velocity_score": sales_velocity_ratio,
            "sold_listings_count": sold_count,
            "active_listings_count": active_count,
            "is_viable_opportunity": is_viable_opportunity
        }


if __name__ == "__main__":
    engine = ArbitrageEngine()
    metrics = engine.calculate_arbitrage_metrics(listing_price=380.0, predicted_market_price=650.0, shipping_fee=14.99, sold_count=24, active_count=6)
    print(" Arbitrage Engine Net Metrics:", metrics)

import pytest

def calculer_marge_nette(prix_achat, frais_port, juste_prix_predit):
    """
    Fonction de test simulant le moteur d'arbitrage.
    Frais eBay : 13.25% du juste prix + 0.30$
    """
    frais_ebay = (juste_prix_predit * 0.1325) + 0.30
    cout_total = prix_achat + frais_port + frais_ebay
    marge_nette = juste_prix_predit - cout_total
    return round(marge_nette, 2)

def test_calcul_marge_nette_positif():
    # Cas d'usage : Achat 100$, Port 10$, Revente 200$
    # Frais eBay attendus : (200 * 0.1325) + 0.30 = 26.80$
    # Cout total : 100 + 10 + 26.80 = 136.80$
    # Marge attendue : 200 - 136.80 = 63.20$
    marge = calculer_marge_nette(100, 10, 200)
    assert marge == 63.20

def test_calcul_marge_nette_negatif():
    # Cas d'usage : Achat 150$, Port 20$, Revente 180$
    # Frais eBay : (180 * 0.1325) + 0.30 = 24.15$
    # Cout total : 150 + 20 + 24.15 = 194.15$
    # Marge attendue : 180 - 194.15 = -14.15$
    marge = calculer_marge_nette(150, 20, 180)
    assert marge == -14.15

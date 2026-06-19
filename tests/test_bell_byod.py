import pytest
from configs.bell_config import CONFIG, SELECTORS
from frameworks.landing_nav_framework import LandingNavigationFramework
from frameworks.checkout_flow_framework import CheckoutFlowFramework

@pytest.mark.parametrize("sim_type", ["esim", "psim"])
def test_full_bell_checkout_flow(automation_env, sim_type, has_upc):
    utils = automation_env
    
    nav = LandingNavigationFramework(utils, CONFIG, SELECTORS)
    checkout = CheckoutFlowFramework(utils, CONFIG)
    
    nav.open_site()
    nav.navigate_byod()
    nav.bell_byod_sb(sim_type=sim_type, has_upc=has_upc)
    
    nav._bell_enter_cart()
    nav.enter_checkout()
    
    if sim_type == "esim":
        checkout.esim_checkout_flow()
    else:
        checkout.psim_checkout_flow()
    
    assert "OrderReview" in utils.driver.current_url
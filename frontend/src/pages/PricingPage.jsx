import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { createSubscriptionCheckout, getMyBillingStatus } from "../api/billingApi";
import { loadRazorpayCheckout } from "../utils/loadRazorpayCheckout";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";

const CONFIRM_POLL_INTERVAL_MS = 1500;
const CONFIRM_POLL_MAX_ATTEMPTS = 8;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const PLANS = [
  {
    key: "free",
    name: "Free",
    price: "₹0",
    period: "one-time trial",
    interviews: 1,
    tailorings: 2,
    cta: "Start Free Trial",
  },
  {
    key: "starter",
    name: "Starter",
    price: "₹199",
    period: "/month",
    interviews: 3,
    tailorings: 5,
    cta: "Upgrade to Starter",
  },
  {
    key: "pro",
    name: "Pro",
    price: "₹549",
    period: "/month",
    interviews: 10,
    tailorings: 15,
    cta: "Upgrade to Pro",
    highlighted: true,
  },
  {
    key: "max",
    name: "Max",
    price: "₹1,299",
    period: "/month",
    interviews: 30,
    tailorings: 50,
    cta: "Upgrade to Max",
  },
];

function PricingPage() {
  const { isAuthenticated, token, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const limitReachedFeature = location.state?.limitReachedFeature;

  const [upgradeError, setUpgradeError] = useState("");
  const [upgradingPlan, setUpgradingPlan] = useState(null);
  const [confirming, setConfirming] = useState(false);

  // The Checkout widget's own success callback only means Razorpay
  // accepted the payment client-side - our DB only reflects the new
  // plan once Razorpay's subscription.activated webhook reaches our
  // server (async, server-to-server, not on this request/response
  // cycle at all). So after Checkout reports success, poll /billing/me
  // for a few seconds waiting for the webhook to land before routing
  // to the dashboard - same "poll until the async backend catches up"
  // pattern already used for resume-analysis progress.
  const waitForPlanActivation = async (expectedPlan) => {
    setConfirming(true);

    for (let attempt = 0; attempt < CONFIRM_POLL_MAX_ATTEMPTS; attempt += 1) {
      try {
        const status = await getMyBillingStatus(token);
        if (status.plan === expectedPlan) {
          setConfirming(false);
          navigate("/dashboard");
          return;
        }
      } catch {
        // keep polling - a transient failure here shouldn't block
      }

      await sleep(CONFIRM_POLL_INTERVAL_MS);
    }

    setConfirming(false);
    setUpgradeError(
      "Payment received - it's taking a little longer than usual to " +
        "activate. Refresh the dashboard in a moment."
    );
  };

  const handleUpgrade = async (plan) => {
    if (!isAuthenticated) {
      navigate("/signup");
      return;
    }

    try {
      setUpgradingPlan(plan);
      setUpgradeError("");

      const checkout = await createSubscriptionCheckout(plan, token);

      const Razorpay = await loadRazorpayCheckout();

      const razorpayInstance = new Razorpay({
        key: checkout.razorpay_key_id,
        subscription_id: checkout.razorpay_subscription_id,
        name: "HotSeat",
        description: `${plan[0].toUpperCase()}${plan.slice(1)} plan`,
        prefill: {
          name: user?.username,
          email: user?.email,
        },
        theme: {
          color: "#e05d38",
        },
        handler: () => {
          waitForPlanActivation(plan);
        },
        modal: {
          ondismiss: () => {
            setUpgradingPlan(null);
          },
        },
      });

      razorpayInstance.on("payment.failed", (response) => {
        setUpgradeError(
          response?.error?.description || "Payment failed."
        );
        setUpgradingPlan(null);
      });

      razorpayInstance.open();
    } catch (err) {
      setUpgradeError(
        err?.response?.data?.detail ||
          "Upgrades aren't available yet - payment isn't configured."
      );
      setUpgradingPlan(null);
    }
  };

  return (
    <div className="dashboard-page">
      <Navbar />

      <main className="dashboard-container">
        {limitReachedFeature && (
          <div className="upgrade-prompt">
            <p className="upgrade-prompt__message">
              <strong>{limitReachedFeature}</strong> has reached its max
              limit for your current plan. Upgrade to use more of it.
            </p>
          </div>
        )}

        <div className="section-header section-header--centered">
          <div className="eyebrow">PRICING</div>
          <h1>Pick a plan.</h1>
          <p>
            Every plan includes a fixed number of interviews and resume-JD
            tailorings per month. Once you use them up, you&apos;ll need to
            upgrade to keep going.
          </p>
        </div>

        <div className="pricing-grid">
          {PLANS.map((plan) => (
            <div
              key={plan.key}
              className={`pricing-card ${
                plan.highlighted ? "pricing-card--highlighted" : ""
              }`}
            >
              <div className="pricing-card__name">{plan.name}</div>
              <div className="pricing-card__price">
                {plan.price}
                <span className="pricing-card__period">{plan.period}</span>
              </div>

              <ul className="pricing-card__features">
                <li>{plan.interviews} interviews</li>
                <li>{plan.tailorings} resume-JD tailorings</li>
              </ul>

              {plan.key === "free" ? (
                <Link
                  to={isAuthenticated ? "/dashboard" : "/signup"}
                  className="button button--primary button--wide"
                >
                  {isAuthenticated ? "Go to dashboard" : plan.cta}
                </Link>
              ) : (
                <button
                  type="button"
                  className="button button--secondary button--wide"
                  disabled={upgradingPlan === plan.key}
                  onClick={() => handleUpgrade(plan.key)}
                >
                  {upgradingPlan === plan.key
                    ? confirming
                      ? "Confirming payment..."
                      : "Please wait..."
                    : plan.cta}
                </button>
              )}
            </div>
          ))}
        </div>

        {upgradeError && <p className="error-text">{upgradeError}</p>}
      </main>
    </div>
  );
}

export default PricingPage;

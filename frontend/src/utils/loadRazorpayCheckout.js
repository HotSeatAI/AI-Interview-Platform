const CHECKOUT_SRC = "https://checkout.razorpay.com/v1/checkout.js";

let loadPromise = null;

// Loads Razorpay's hosted Checkout script exactly once, however many
// times this is called - subsequent calls reuse the same in-flight/
// resolved promise instead of injecting duplicate <script> tags.
export function loadRazorpayCheckout() {
  if (window.Razorpay) {
    return Promise.resolve(window.Razorpay);
  }

  if (loadPromise) {
    return loadPromise;
  }

  loadPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = CHECKOUT_SRC;
    script.onload = () => resolve(window.Razorpay);
    script.onerror = () => {
      loadPromise = null;
      reject(new Error("Failed to load Razorpay Checkout."));
    };
    document.body.appendChild(script);
  });

  return loadPromise;
}

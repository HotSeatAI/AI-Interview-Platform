import logoIcon from "../../assets/logo-icon.png";

function BrandLogo({ className = "" }) {
  return (
    <span className={`brand-logo ${className}`.trim()}>
      <img src={logoIcon} alt="" className="brand-logo__icon" />
      <span className="brand-logo__wordmark">
        <span className="brand-logo__wordmark-hot">Hot</span>
        <span className="brand-logo__wordmark-seat">Seat</span>
      </span>
    </span>
  );
}

export default BrandLogo;

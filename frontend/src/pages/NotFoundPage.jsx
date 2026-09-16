import BrandLogo from "../components/layout/BrandLogo";
import Button from "../components/ui/Button";
import usePageMeta from "../hooks/usePageMeta";

function NotFoundPage() {
  usePageMeta("Page Not Found", "The page you're looking for doesn't exist or may have moved.");

  return (
    <div className="not-found-page">
      <BrandLogo className="not-found-page__brand" />
      <div className="eyebrow">ERROR 404</div>
      <h1 className="not-found-page__title">This page isn't in the schedule.</h1>
      <p className="not-found-page__body">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <Button to="/" variant="primary">
        Go home
      </Button>
    </div>
  );
}

export default NotFoundPage;

import { useEffect } from "react";

function setMetaTag(selector, attribute, attributeValue, content) {
  let tag = document.querySelector(selector);
  if (!tag) {
    tag = document.createElement("meta");
    tag.setAttribute(attribute, attributeValue);
    document.head.appendChild(tag);
  }
  tag.setAttribute("content", content);
}

function usePageMeta(title, description) {
  useEffect(() => {
    const fullTitle = title ? `${title} · HotSeat` : "HotSeat";
    document.title = fullTitle;

    if (description) {
      setMetaTag('meta[name="description"]', "name", "description", description);
      setMetaTag('meta[property="og:description"]', "property", "og:description", description);
      setMetaTag('meta[name="twitter:description"]', "name", "twitter:description", description);
    }

    setMetaTag('meta[property="og:title"]', "property", "og:title", fullTitle);
    setMetaTag('meta[name="twitter:title"]', "name", "twitter:title", fullTitle);
  }, [title, description]);
}

export default usePageMeta;

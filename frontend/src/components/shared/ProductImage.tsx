import { useEffect, useState } from "react";

const CATEGORY_EMOJI: Record<string, string> = {
  Clothing: "👕",
  Shoes: "👟",
  Bags: "👜",
  Accessories: "⌚",
  Furniture: "🪑",
  Home: "🏠",
  Kitchen: "🍳",
  Beauty: "✨",
  Fitness: "🏋️",
  Tech: "💻",
  General: "🌿",
};

type Props = {
  src: string;
  alt: string;
  className?: string;
  placeholderClassName?: string;
  category?: string;
};

export default function ProductImage({
  src,
  alt,
  className = "productImage",
  placeholderClassName,
  category = "General",
}: Props) {
  const [broken, setBroken] = useState(!src);

  useEffect(() => {
    setBroken(!src);
  }, [src]);

  if (broken) {
    return (
      <div className={`productImagePlaceholder ${placeholderClassName ?? className}`}>
        <span className="productImagePlaceholderIcon">
          {CATEGORY_EMOJI[category] ?? "🌿"}
        </span>
        <span className="productImagePlaceholderLabel">{category}</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      referrerPolicy="no-referrer"
      loading="lazy"
      decoding="async"
      onError={() => setBroken(true)}
    />
  );
}

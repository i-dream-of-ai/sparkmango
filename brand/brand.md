# Spark Mango — Visual Identity Guide

A clean, playful, developer-friendly visual identity designed for readability, nighttime use, and a consistent interface. This guide helps anyone creating UI components, documentation, websites, or other branded assets maintain a cohesive visual language.

---

## ✨ Color Palette

| Color Role           | Hex       | RGB             | Notes |
|----------------------|-----------|------------------|-------|
| **Primary Orange**   | `#FFA629` | rgb(255, 166, 41) | Main highlight & mango color |
| **Spark Yellow**     | `#FFE156` | rgb(255, 225, 86) | Accent for spark visuals |
| **Leaf Green**       | `#59C173` | rgb(89, 193, 115) | Mango leaf; use for minor highlights |
| **Charcoal BG**      | `#1E1E1E` | rgb(30, 30, 30)   | Main background (dark mode dev-friendly) |
| **Warm Brown**       | `#6F4E37` | rgb(111, 78, 55)  | Optional secondary background or outline |
| **Soft Off-White**   | `#F4F4F4` | rgb(244, 244, 244) | Primary text color |

---

## 🔤 Typography

| Usage             | Font             | Backup Fonts                     | Style |
|------------------|------------------|----------------------------------|-------|
| Headings         | `Inter`          | `-apple-system`, `sans-serif`    | Bold, clean, readable |
| Body / Labels     | `Inter`          | `system-ui`, `sans-serif`        | Medium or Regular |
| Code / Inline UI | `JetBrains Mono` | `Menlo`, `monospace`             | Optional for dev tools |

**Download Inter:** [https://fonts.google.com/specimen/Inter](https://fonts.google.com/specimen/Inter)

> ✅ *Inter is free, legible, and widely supported. It closely matches the lowercase logo aesthetic.*

---

## 📐 Layout & Sizing

To create a clean and visually pleasant experience, follow these guidelines:

### Base Units
- **Base Spacing Unit:** `8px`  
- Use multiples of 8px for spacing: `8px`, `16px`, `24px`, `32px`, `64px`, etc.

### Text Sizes
| Text Type     | Size     | Weight | Notes |
|---------------|----------|--------|-------|
| h1            | 40px     | 700    | Page titles |
| h2            | 32px     | 700    | Section headers |
| h3            | 24px     | 600    | Subheadings |
| Body Large    | 18px     | 400–500| Comfortable reading |
| Body Regular  | 16px     | 400    | Default paragraph |
| Caption       | 12–14px  | 400    | Notes, UI labels |

---

## 🧩 UI Styling Guidelines

### Borders and Lines
- Use **1px** solid lines in `#FFA629` (orange) for dividers or accent separators
- Maintain **8px** or **16px** padding above/below each divider

### Containers
- Rounded corners: `12px`
- Shadow for floating elements:
```css
box-shadow: 0 4px 12px rgba(0,0,0,0.15);

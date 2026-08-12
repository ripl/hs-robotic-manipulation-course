# Publication Checklist

Use this checklist before pushing public course updates to the TTIC website or GitHub Pages.

## Content

- Course overview is current.
- Module pages have goals, duration, prerequisites, materials, and links.
- Slides and source documents are linked from [Resources](../resources.md).
- Teacher-only notes are clearly labeled or kept out of the public navigation.
- Answer keys and solution-only code are intentionally included or intentionally excluded.

## Privacy and Attribution

- Student names, addresses, phone numbers, and private schedules are removed.
- Images of students have permission for public use.
- External diagrams or images have acceptable licensing or are replaced.
- Borrowed assignments include attribution.

## Technical

- `mkdocs build --strict` passes.
- Links to repository files work.
- Download assets open correctly.
- The site is readable on mobile.
- Hardware safety notes are visible before motor-control instructions.

## Deployment

The included GitHub Actions workflow builds the site and deploys it to GitHub Pages after pushes to `main`. TTIC can either link to that site, configure a TTIC subdomain, or host the generated static `site/` directory on TTIC infrastructure.

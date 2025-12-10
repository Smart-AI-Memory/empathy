interface TestsBadgeProps {
  tests?: number;
  coverage?: number;
}

export default function TestsBadge({
  tests = 1954,
  coverage = 90.12
}: TestsBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-[#10B981] text-white">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <span>
        {tests.toLocaleString()} tests | {coverage.toFixed(0)}% coverage
      </span>
    </span>
  );
}

import RestorationShell from "../components/RestorationShell.jsx";

export default function Universal() {
  return <RestorationShell title="Universal Restoration"
    subtitle="One autoencoder restores clean, noisy, blurred and occluded images without being told the corruption type."
    endpoint="/restore/universal" />;
}

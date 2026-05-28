import { notFound } from "next/navigation";
import { CropStatsContent } from "@/components/crops/CropStatsContent";
import { MOCK_CROPS, getCropHistory, getCropStats } from "@/lib/mock-data";

type Props = { params: Promise<{ id: string }> };

export default async function CropStatsPage({ params }: Props) {
  const { id } = await params;
  const crop = MOCK_CROPS.find((c) => c.id === id);
  if (!crop) notFound();

  return (
    <CropStatsContent
      crop={crop}
      history={getCropHistory(id)}
      stats={getCropStats(id)}
      context="user"
    />
  );
}

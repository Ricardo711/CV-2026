import { api } from "./http";

export type LabeledImage = {
  id: string;
  image_url: string;
  marbling_class: string;
  created_at: string;
};

export async function uploadLabeledImage(
  file: File,
  marbling_class: string,
): Promise<LabeledImage> {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("marbling_class", marbling_class);

  return api<LabeledImage>("/api/images", { method: "POST", body: fd });
}
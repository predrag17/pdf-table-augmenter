import axiosInstance from "@/config/axiosInstance";

export const extractTablesFromFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axiosInstance.post(
      "/extract-description",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  } catch (error: any) {
    console.error("Error fetching categories", error);
    throw error;
  }
};

import axiosInstance from "@/config/axiosInstance";

export const extractTablesFromFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axiosInstance.post(
      "/extract-description/tables",
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

export const extractImagesFromFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axiosInstance.post(
      "/extract-description/images",
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

export const extractFormulasFromFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axiosInstance.post(
      "/extract-description/formulas",
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

export const askQuestion = async (question: string, description: string) => {
  try {
    const response = await axiosInstance.post(
      "/ask-question",
      {
        question,
        table_description: description,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return response.data;
  } catch (error: any) {
    console.error("Error fetching answer", error);
    throw error;
  }
};


import Box from "@mui/material/Box";
import { Chip, Typography, useTheme } from "@mui/material";
import { useDropzone } from "react-dropzone";

const MediaCard = () => {
  const theme = useTheme();

  const { acceptedFiles, getRootProps, getInputProps } = useDropzone();

  const files = acceptedFiles.map((file: any) => (
    <Box
      key={file.path}
      display="flex"
      alignItems="center"
      py={1}
      mt={2}
      sx={{ borderTop: `1px solid ${theme.palette.divider}` }}
      justifyContent="space-between"
    >
      <Typography variant="body1" fontWeight="500">
        {file.path}{" "}
      </Typography>
      <Chip color="primary" label={`${file.size} Bytes`} />
    </Box>
  ));

  return (
    <Box p={3}>
      <Typography variant="h5">Media</Typography>

      <Box
        mt={3}
        fontSize="12px"
        sx={{
          backgroundColor: "primary.light",
          color: "primary.main",
          padding: "40px 30px",
          textAlign: "center",
          border: `1px dashed`,
          borderColor: "primary.main",
        }}
        {...getRootProps({ className: "dropzone" })}
      >
        <input {...getInputProps()} />
        <p>Drag 'n' drop some files here, or click to select files</p>
      </Box>
      <Box mt={2}>
        <Typography variant="h6" fontSize="15px">
          Files :
        </Typography>
        <Typography variant="body1">{files}</Typography>
      </Box>
    </Box>
  );
};

export default MediaCard;

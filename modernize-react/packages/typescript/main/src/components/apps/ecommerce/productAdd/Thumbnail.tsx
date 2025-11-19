
import Box from "@mui/material/Box";
import { Typography, useTheme, Chip } from "@mui/material";
import { useDropzone } from "react-dropzone";

const Thumbnail = () => {
  const theme = useTheme();

  const { acceptedFiles, getRootProps, getInputProps } = useDropzone();

  const files = acceptedFiles.map((file: File, i) => (
    <Box
      key={i}
      display="flex"
      alignItems="center"
      py={1}
      mt={2}
      sx={{ borderTop: `1px solid ${theme.palette.divider}` }}
      justifyContent="space-between"
    >
      <Typography variant="body1" fontWeight="500">
        {file.name}{" "}
      </Typography>
      <Chip color="primary" label={`${file.size} Bytes`} />
    </Box>
  ));

  return (
    <Box p={3}>
      <Typography variant="h5">Thumbnail</Typography>

      <Box
        mt={3}
        fontSize="12px"
        sx={{
          backgroundColor: "primary.light",
          color: "primary.main",
          padding: "30px",
          textAlign: "center",
          border: `1px dashed`,
          borderColor: "primary.main",
        }}
        {...getRootProps({ className: "dropzone" })}
      >
        <input {...getInputProps()} />
        <p>Drag 'n' drop some files here, or click to select files</p>
      </Box>
      <Typography variant="body2" textAlign="center" mt={1}>
        Set the product thumbnail image. Only *.png, *.jpg and *.jpeg image
        files are accepted.
      </Typography>
      <Box mt={2}>
        <Typography variant="h6" fontSize="15px">
          Files
        </Typography>
        <Typography variant="body1">{files}</Typography>
      </Box>
    </Box>
  );
};

export default Thumbnail;

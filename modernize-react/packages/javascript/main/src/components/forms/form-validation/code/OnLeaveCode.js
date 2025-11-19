import CodeDialog from '../../../shared/CodeDialog';

const OnLeaveCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { styled } from '@mui/material/styles';
import { TextField } from '@mui/material';
import { Typography } from '@mui/material';

import { Box, Button, Stack } from '@mui/material';

const CustomTextField = styled((props) => <TextField {...props} />)(({ theme }) => ({
  '& .MuiOutlinedInput-input::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '0.8',
  },
  '& .MuiOutlinedInput-input.Mui-disabled::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '1',
  },
  '& .Mui-disabled .MuiOutlinedInput-notchedOutline': {
    borderColor: theme.palette.grey[200],
  },
}));

const CustomFormLabel = styled((props) => (
  <Typography
    variant="subtitle1"
    fontWeight={600}
    {...props}
    component="label"
    htmlFor={props.htmlFor}
  />
))(() => ({
  marginBottom: '5px',
  marginTop: '25px',
  display: 'block',
}));

const validationSchema = yup.object({
    emailInstant: yup.string().email('Enter a valid email').required('Email is required'),
    passwordInstant: yup.string().min(8, 'Password should be of minimum 8 characters length').required('Password is required')
});


const formik = useFormik({
    initialValues: {
        emailInstant: '',
        passwordInstant: ''
    },
    validationSchema,
});

  return (
    <form onSubmit={formik.handleSubmit}>
      <Stack>
        <Box mt="-10px">
          <CustomFormLabel>Email Address</CustomFormLabel>
          <CustomTextField
            fullWidth
            id="emailInstant"
            name="emailInstant"
            value={formik.values.emailInstant}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.emailInstant && Boolean(formik.errors.emailInstant)}
            helperText={formik.touched.emailInstant && formik.errors.emailInstant}
          />
        </Box>
        <Box mb={3}>
          <CustomFormLabel>Password</CustomFormLabel>
          <CustomTextField
            fullWidth
            id="passwordInstant"
            name="passwordInstant"
            type="password"
            value={formik.values.passwordInstant}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.passwordInstant && Boolean(formik.errors.passwordInstant)}
            helperText={formik.touched.passwordInstant && formik.errors.passwordInstant}
          />
        </Box>
        <Stack direction="row" justifyContent="flex-end">
          <Button variant="contained" type="submit">
            Submit
          </Button>
        </Stack>
      </Stack>
    </form>
  );

`}
      </CodeDialog>
    </>
  );
};

export default OnLeaveCode;

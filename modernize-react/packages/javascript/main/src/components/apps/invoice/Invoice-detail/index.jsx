import React, { useContext, useEffect, useState } from 'react';
import { InvoiceContext } from 'src/context/InvoiceContext/index';
import { useLocation } from 'react-router';
import {
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Stack,
  Chip,
  Divider,
} from '@mui/material';
import { Grid } from '@mui/material';
import { format, isValid, parseISO } from 'date-fns';
import { Link } from 'react-router';
import Logo from 'src/layouts/full/shared/logo/Logo';

const InvoiceDetail = () => {
  const { invoices } = useContext(InvoiceContext);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    // Set the first invoice as the default selected invoice initially
    if (invoices.length > 0) {
      setSelectedInvoice(invoices[0]);
    }
  }, [invoices]);

  // Get the last part of the URL path as the billFrom parameter
  const title = useLocation();
  const getTitle = title.pathname.split('/').pop();

  // Find the invoice that matches the billFrom extracted from the URL
  useEffect(() => {
    if (getTitle) {
      const invoice = invoices.find((p) => p.billFrom === getTitle);
      if (invoice) {
        setSelectedInvoice(invoice);
      }
    }
  }, [getTitle, invoices]);

  if (!selectedInvoice) {
    return <div>Loading...</div>;
  }

  const orderDate = selectedInvoice.orderDate
    ? isValid(parseISO(selectedInvoice.orderDate))
      ? format(parseISO(selectedInvoice.orderDate), 'EEEE, MMMM dd, yyyy')
      : 'Invalid Date'
    : format(new Date(), 'EEEE, MMMM dd, yyyy');

  return (
    <>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        alignItems="center"
        justifyContent="space-between"
        mb={2}
      >
        <Box
          sx={{
            textAlign: {
              xs: 'center',
              sm: 'left',
            },
          }}
        >
          <Typography variant="h5"># {selectedInvoice.id}</Typography>
          <Box mt={1}>
            <Chip size="small" color="secondary" variant="outlined" label={orderDate}></Chip>
          </Box>
        </Box>

        <Logo />
        <Box textAlign="right">
          {selectedInvoice.status === 'Shipped' ? (
            <Chip size="small" color="primary" label={selectedInvoice.status} />
          ) : selectedInvoice.status === 'Delivered' ? (
            <Chip size="small" color="success" label={selectedInvoice.status} />
          ) : selectedInvoice.status === 'Pending' ? (
            <Chip size="small" color="warning" label={selectedInvoice.status} />
          ) : (
            ''
          )}
        </Box>
      </Stack>
      <Divider></Divider>

      <Grid container spacing={3} mt={2} mb={4}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <Paper variant="outlined">
            <Box p={3} display="flex" flexDirection="column" gap="4px">
              <Typography variant="h6" mb={2}>
                From :
              </Typography>
              <Typography variant="body1">{selectedInvoice.billFrom}</Typography>
              <Typography variant="body1">{selectedInvoice.billFromEmail}</Typography>
              <Typography variant="body1">{selectedInvoice.billFromAddress}</Typography>
              <Typography variant="body1">{selectedInvoice.billFromPhone}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <Paper variant="outlined">
            <Box p={3} display="flex" flexDirection="column" gap="4px">
              <Typography variant="h6" mb={2}>
                To :
              </Typography>
              <Typography variant="body1">{selectedInvoice.billTo}</Typography>
              <Typography variant="body1">{selectedInvoice.billToEmail}</Typography>
              <Typography variant="body1">{selectedInvoice.billToAddress}</Typography>
              <Typography variant="body1">{selectedInvoice.billToPhone}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Paper variant="outlined">
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <Typography variant="h6" fontSize="14px">
                    Item Name
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6" fontSize="14px">
                    Unit Price
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6" fontSize="14px">
                    Unit
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="h6" fontSize="14px">
                    Total Cost
                  </Typography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {selectedInvoice.orders.map((order, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Typography variant="body1">{order.itemName}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body1">{order.unitPrice}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body1">{order.units}</Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1">{order.unitTotalPrice}</Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
      <Box p={3} bgcolor="primary.light" mt={3}>
        <Box display="flex" justifyContent="end" gap={3} mb={3}>
          <Typography variant="body1" fontWeight={600}>
            Sub Total:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {selectedInvoice.totalCost}
          </Typography>
        </Box>
        <Box display="flex" justifyContent="end" gap={3} mb={3}>
          <Typography variant="body1" fontWeight={600}>
            Vat:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {selectedInvoice.vat}
          </Typography>
        </Box>
        <Box display="flex" justifyContent="end" gap={3}>
          <Typography variant="body1" fontWeight={600}>
            Grand Total:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {selectedInvoice.grandTotal}
          </Typography>
        </Box>
      </Box>
      <Box display="flex" alignItems="center" gap={1} mt={3} justifyContent="end">
        <Button
          variant="contained"
          color="secondary"
          component={Link}
          to={`/apps/invoice/edit/${selectedInvoice.billFrom}`}
        >
          Edit Invoice
        </Button>
        <Button variant="contained" color="primary" component={Link} to="/apps/invoice/list">
          Back to Invoice List
        </Button>
      </Box>
    </>
  );
};

export default InvoiceDetail;

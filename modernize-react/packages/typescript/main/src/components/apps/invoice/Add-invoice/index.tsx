
import React, { useState, useContext, useEffect } from 'react';
import { InvoiceContext } from 'src/context/InvoiceContext';
import {
  Alert,
  Button,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Box,
  Stack,
  Divider,
  Grid,
} from '@mui/material';
import { useNavigate } from 'react-router';
import { format, isValid } from 'date-fns';
import { IconPlus, IconSquareRoundedPlus, IconTrash } from '@tabler/icons-react';
import CustomFormLabel from 'src/components/forms/theme-elements/CustomFormLabel';
import CustomSelect from 'src/components/forms/theme-elements/CustomSelect';
import CustomTextField from 'src/components/forms/theme-elements/CustomTextField';

const CreateInvoice = () => {
  const { addInvoice, invoices } = useContext(InvoiceContext);
  const [showAlert, setShowAlert] = useState(false);
  const router = useNavigate();
  const [formData, setFormData] = useState({
    id: 0,
    billFrom: '',
    billTo: '',
    totalCost: 0,
    status: 'Pending',
    billFromAddress: '',
    billToAddress: '',
    orders: [{ itemName: '', unitPrice: '', units: '', unitTotalPrice: 0 }],
    vat: 0,
    grandTotal: 0,
    subtotal: 0,
    date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    if (invoices.length > 0) {
      const lastId = invoices[invoices.length - 1].id;
      setFormData((prevData: any) => ({
        ...prevData,
        id: lastId + 1,
      }));
    } else {
      setFormData((prevData: any) => ({
        ...prevData,
        id: 1,
      }));
    }
  }, [invoices]);

  const calculateTotals = (orders: any[]) => {
    let subtotal = 0;

    orders.forEach((order) => {
      const unitPrice = parseFloat(order.unitPrice) || 0;
      const units = parseInt(order.units) || 0;
      const totalCost = unitPrice * units;

      subtotal += totalCost;
      order.unitTotalPrice = totalCost;
    });

    const vat = subtotal * 0.1;
    const grandTotal = subtotal + vat;

    return { subtotal, vat, grandTotal };
  };

  const handleChange = (e: { target: { name: any; value: any } }) => {
    const { name, value } = e.target;
    setFormData((prevData) => {
      const newFormData = { ...prevData, [name]: value };
      const totals = calculateTotals(newFormData.orders);
      return {
        ...newFormData,
        ...totals,
      };
    });
  };

  const handleOrderChange = (index: number, field: string, value: string) => {
    setFormData((prevData) => {
      const updatedOrders = [...prevData.orders];
      updatedOrders[index] = {
        ...updatedOrders[index],
        [field]: value,
      };
      const totals = calculateTotals(updatedOrders);
      return {
        ...prevData,
        orders: updatedOrders,
        ...totals,
      };
    });
  };

  const handleAddItem = () => {
    setFormData((prevData) => {
      const updatedOrders = [
        ...prevData.orders,
        { itemName: '', unitPrice: '', units: '', unitTotalPrice: 0 },
      ];
      const totals = calculateTotals(updatedOrders);
      return {
        ...prevData,
        orders: updatedOrders,
        ...totals,
      };
    });
  };

  const handleDeleteItem = (index: number) => {
    setFormData((prevData) => {
      const updatedOrders = prevData.orders.filter((_, i) => i !== index);
      const totals = calculateTotals(updatedOrders);
      return {
        ...prevData,
        orders: updatedOrders,
        ...totals,
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addInvoice(formData);
      setFormData({
        id: 0,
        billFrom: '',
        billTo: '',
        totalCost: 0,
        status: 'Pending',
        billFromAddress: '',
        billToAddress: '',
        orders: [{ itemName: '', unitPrice: '', units: '', unitTotalPrice: 0 }],
        vat: 0,
        grandTotal: 0,
        subtotal: 0,
        date: new Date().toISOString().split('T')[0],
      });
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
      }, 5000);
      router('/apps/invoice/list');
    } catch (error) {
      console.error('Error adding invoice:', error);
    }
  };

  const parsedDate = isValid(new Date(formData.date)) ? new Date(formData.date) : new Date();
  const formattedOrderDate = format(parsedDate, 'EEEE, MMMM dd, yyyy');

  return (<>
    <form onSubmit={handleSubmit}>
      <Box>
        <Stack
          direction="row"
          spacing={{ xs: 1, sm: 2, md: 4 }}
          justifyContent="space-between"
          mb={3}
        >
          <Typography variant="h5"># {formData.id}</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              color="error"
              onClick={() => {
                router('/apps/invoice/list');
              }}
            >
              Cancel
            </Button>
            <Button type="submit" variant="contained" color="primary">
              Create Invoice
            </Button>
          </Box>
        </Stack>
        <Divider></Divider>
        <Stack
          direction="row"
          spacing={{ xs: 1, sm: 2, md: 4 }}
          justifyContent="space-between"
          alignItems="center"
          mb={3}
        >
          <Box>
            <CustomFormLabel htmlFor="demo-simple-select">Order Status</CustomFormLabel>

            <CustomSelect
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              value={formData.status}
              onChange={handleChange}
              disabled
            >
              <MenuItem value="Pending">Pending</MenuItem>
              <MenuItem value="Shipped">Shipped</MenuItem>
              <MenuItem value="Delivered">Delivered</MenuItem>
            </CustomSelect>
          </Box>
          <Box textAlign="right">
            <CustomFormLabel htmlFor="demo-simple-select">Order Date</CustomFormLabel>
            <Typography variant="body1"> {formattedOrderDate}</Typography>
          </Box>
        </Stack>
        <Divider></Divider>

        <Grid container spacing={3} mb={4}>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            <CustomFormLabel htmlFor="bill-from">Bill From</CustomFormLabel>
            <CustomTextField
              id="bill-from"
              name="billFrom"
              value={formData.billFrom}
              onChange={handleChange}
              fullWidth
            />
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            <CustomFormLabel
              htmlFor="bill-to"
              sx={{
                mt: {
                  xs: 0,
                  sm: 3,
                },
              }}
            >
              Bill To
            </CustomFormLabel>
            <CustomTextField
              name="billTo"
              value={formData.billTo}
              onChange={handleChange}
              fullWidth
            />
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            <CustomFormLabel
              htmlFor="From Address"
              sx={{
                mt: 0,
              }}
            >
              From Address
            </CustomFormLabel>
            <CustomTextField
              name="billFromAddress"
              value={formData.billFromAddress}
              onChange={handleChange}
              fullWidth
            />
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            <CustomFormLabel
              htmlFor="Bill To Address"
              sx={{
                mt: 0,
              }}
            >
              Bill To Address
            </CustomFormLabel>
            <CustomTextField
              name="billToAddress"
              value={formData.billToAddress}
              onChange={handleChange}
              fullWidth
            />
          </Grid>
        </Grid>
        {/* Orders Table */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Items Details :</Typography>
          <Button
            onClick={handleAddItem}
            variant="contained"
            color="primary"
            startIcon={<IconPlus width={18} />}
          >
            Add Item
          </Button>
        </Stack>

        <Paper variant="outlined">
          <TableContainer sx={{ whiteSpace: { xs: 'nowrap', md: 'unset' } }}>
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
                      Units
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="h6" fontSize="14px">
                      Total Cost
                    </Typography>
                  </TableCell>
                  <TableCell></TableCell>
                  <TableCell>
                    <Typography variant="h6" fontSize="14px">
                      Actions
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {formData.orders.map((order, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <CustomTextField
                        type="text"
                        value={order.itemName}
                        placeholder="Item Name"
                        onChange={(e: any) =>
                          handleOrderChange(index, 'itemName', e.target.value)
                        }
                        fullWidth
                      />
                    </TableCell>
                    <TableCell>
                      <CustomTextField
                        type="number"
                        value={order.unitPrice}
                        placeholder="Unit Price"
                        onChange={(e: any) =>
                          handleOrderChange(index, 'unitPrice', e.target.value)
                        }
                        fullWidth
                      />
                    </TableCell>
                    <TableCell>
                      <CustomTextField
                        type="number"
                        value={order.units}
                        placeholder="Units"
                        onChange={(e: any) => handleOrderChange(index, 'units', e.target.value)}
                        fullWidth
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1">{order.unitTotalPrice}</Typography>
                    </TableCell>
                    <TableCell></TableCell>
                    <TableCell>
                      <Tooltip title="Add Item">
                        <IconButton onClick={handleAddItem} color="primary">
                          <IconSquareRoundedPlus width={22} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Item">
                        <IconButton onClick={() => handleDeleteItem(index)} color="error">
                          <IconTrash width={22} />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Totals */}
        <Box p={3} bgcolor="primary.light" mt={3}>
          <Box display="flex" justifyContent="end" gap={3} mb={3}>
            <Typography variant="body1" fontWeight={600}>
              Sub Total:
            </Typography>
            <Typography variant="body1" fontWeight={600}>
              {formData.subtotal}
            </Typography>
          </Box>
          <Box display="flex" justifyContent="end" gap={3} mb={3}>
            <Typography variant="body1" fontWeight={600}>
              VAT:
            </Typography>
            <Typography variant="body1" fontWeight={600}>
              {formData.vat}
            </Typography>
          </Box>
          <Box display="flex" justifyContent="end" gap={3}>
            <Typography variant="body1" fontWeight={600}>
              Grand Total:
            </Typography>
            <Typography variant="body1" fontWeight={600}>
              {formData.grandTotal}
            </Typography>
          </Box>
        </Box>

        {showAlert && (
          <Alert severity="success" sx={{ position: 'fixed', top: 16, right: 16 }}>
            Invoice added successfully.
          </Alert>
        )}
      </Box>
    </form>
  </>);
};

export default CreateInvoice;

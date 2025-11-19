
import { useContext, useState, useEffect } from 'react';
import { InvoiceContext } from 'src/context/InvoiceContext/index';
import { useLocation, useNavigate } from 'react-router';
import {
  Button,
  MenuItem,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  IconButton,
  Tooltip,
  Box,
  Stack,
  Divider,
  Grid,
} from '@mui/material';
import { format, isValid } from 'date-fns';
import CustomFormLabel from 'src/components/forms/theme-elements/CustomFormLabel';
import CustomSelect from 'src/components/forms/theme-elements/CustomSelect';
import CustomTextField from 'src/components/forms/theme-elements/CustomTextField';
import { IconSquareRoundedPlus, IconTrash } from '@tabler/icons-react';

const EditInvoicePage = () => {
  const { invoices, updateInvoice } = useContext(InvoiceContext);
  const [showAlert, setShowAlert] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  const [editing, setEditing] = useState(false);
  const [editedInvoice, setEditedInvoice]: any = useState(null);

  const title = useLocation();
  const getTitle = title.pathname.split('/').pop();

  useEffect(() => {
    if (invoices.length > 0) {
      // If there's a specific item to edit, use it
      if (getTitle) {
        const invoice = invoices.find((inv: { billFrom: string }) => inv.billFrom === getTitle);
        if (invoice) {
          setSelectedInvoice(invoice);
          setEditedInvoice({ ...invoice });
          setEditing(true);
        } else {
          // If specific item not found, fallback to default
          setSelectedInvoice(invoices[0]);
          setEditedInvoice({ ...invoices[0] });
          setEditing(true);
        }
      } else {
        // No specific item, default to the first invoice
        setSelectedInvoice(invoices[0]);
        setEditedInvoice({ ...invoices[0] });
        setEditing(true);
      }
    }
  }, [getTitle, invoices]);

  const router = useNavigate();

  const handleSave = async () => {
    try {
      await updateInvoice(editedInvoice);
      setSelectedInvoice({ ...editedInvoice });
      setEditing(false); // Exit editing mode
      setShowAlert(true);

      // Navigate to the list page
      router('/apps/invoice/list');
    } catch (error) {
      console.error('Error updating invoice:', error);
    }

    setTimeout(() => {
      setShowAlert(false);
    }, 5000);
  };

  const handleCancel = () => {
    setEditing(false);
  };

  const handleOrderChange = (
    index: string | number | any,
    field: string,
    value: string | number,
  ) => {
    const updatedOrders = [...editedInvoice.orders];
    updatedOrders[index][field] = value;

    // Calculate unitTotalPrice for the changed item
    if (field === 'unitPrice' || field === 'units') {
      updatedOrders[index].unitTotalPrice =
        updatedOrders[index].unitPrice * updatedOrders[index].units;
    }

    // Update editedInvoice with updated orders and recalculate totals
    const updatedInvoice = {
      ...editedInvoice,
      orders: updatedOrders,
      totalCost: calculateTotalCost(updatedOrders),
      vat: calculateVAT(updatedOrders),
      grandTotal: calculateGrandTotal(
        calculateTotalCost(updatedOrders),
        calculateVAT(updatedOrders),
      ),
    };

    setEditedInvoice(updatedInvoice);
  };

  const handleAddItem = () => {
    const newItem = {
      itemName: '',
      unitPrice: 0,
      units: 0,
      unitTotalPrice: 0,
      vat: 0,
    };
    const updatedOrders = [...editedInvoice.orders, newItem];

    // Update editedInvoice with updated orders and recalculate totals
    const updatedInvoice = {
      ...editedInvoice,
      orders: updatedOrders,
      totalCost: calculateTotalCost(updatedOrders),
      vat: calculateVAT(updatedOrders),
      grandTotal: calculateGrandTotal(
        calculateTotalCost(updatedOrders),
        calculateVAT(updatedOrders),
      ),
    };
    setEditedInvoice(updatedInvoice);
  };

  const handleDeleteItem = (index: any) => {
    const updatedOrders = editedInvoice.orders.filter((_: any, i: any) => i !== index);

    const updatedInvoice = {
      ...editedInvoice,
      orders: updatedOrders,
      totalCost: calculateTotalCost(updatedOrders),
      vat: calculateVAT(updatedOrders),
      grandTotal: calculateGrandTotal(
        calculateTotalCost(updatedOrders),
        calculateVAT(updatedOrders),
      ),
    };
    setEditedInvoice(updatedInvoice);
  };

  const calculateTotalCost = (orders: any[]) => {
    return orders.reduce((total, order) => total + order.unitTotalPrice, 0);
  };

  const calculateVAT = (orders: any[]) => {
    return orders.reduce((totalVAT, order) => totalVAT + order.units, 0);
  };

  const calculateGrandTotal = (totalCost: number, vat: number) => {
    return (totalCost += (totalCost * vat) / 100);
  };

  if (!selectedInvoice) {
    return <div>Please select an invoice.</div>;
  }

  const orderDate = selectedInvoice.orderDate;
  const parsedDate = isValid(new Date(orderDate)) ? new Date(orderDate) : new Date();
  const formattedOrderDate = format(parsedDate, 'EEEE, MMMM dd, yyyy');

  return (
    (<Box>
      <Stack
        direction="row"
        spacing={{ xs: 1, sm: 2, md: 4 }}
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h5"># {editedInvoice.id}</Typography>
        <Box display="flex" gap={1}>
          {editing ? (
            <>
              <Button variant="contained" color="primary" onClick={handleSave}>
                Save
              </Button>
              <Button variant="outlined" color="error" onClick={handleCancel}>
                Cancel
              </Button>
            </>
          ) : (
            <Button variant="contained" color="info" onClick={() => setEditing(true)}>
              Edit Invoice
            </Button>
          )}
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
            value={editedInvoice.status}
            onChange={(e: any) => setEditedInvoice({ ...editedInvoice, status: e.target.value })}
          >
            <MenuItem value="Pending">Pending</MenuItem>
            <MenuItem value="Delivered">Delivered</MenuItem>
            <MenuItem value="Shipped">Shipped</MenuItem>
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
          <CustomFormLabel>Bill From</CustomFormLabel>
          <CustomTextField
            value={editedInvoice.billFrom}
            onChange={(e: any) => setEditedInvoice({ ...editedInvoice, billFrom: e.target.value })}
            fullWidth
          />
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6
          }}>
          <CustomFormLabel
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
            value={editedInvoice.billTo}
            onChange={(e: any) => setEditedInvoice({ ...editedInvoice, billTo: e.target.value })}
            fullWidth
          />
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
          >
            From Address
          </CustomFormLabel>
          <CustomTextField
            value={editedInvoice.billFromAddress}
            onChange={(e: any) =>
              setEditedInvoice({
                ...editedInvoice,
                billFromAddress: e.target.value,
              })
            }
            fullWidth
          />
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
          >
            Bill To Address
          </CustomFormLabel>
          <CustomTextField
            value={editedInvoice.billToAddress}
            onChange={(e: any) =>
              setEditedInvoice({
                ...editedInvoice,
                billToAddress: e.target.value,
              })
            }
            fullWidth
          />
        </Grid>
      </Grid>
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
                <TableCell>
                  <Typography variant="h6" fontSize="14px">
                    Action
                  </Typography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {editedInvoice.orders.map((order: any, index: number) => (
                <TableRow key={index}>
                  <TableCell>
                    <CustomTextField
                      type="text"
                      value={order.itemName}
                      onChange={(e: any) => handleOrderChange(index, 'itemName', e.target.value)}
                      fullWidth
                    />
                  </TableCell>
                  <TableCell>
                    <CustomTextField
                      type="number"
                      value={order.unitPrice}
                      onChange={(e: any) =>
                        handleOrderChange(index, 'unitPrice', parseFloat(e.target.value))
                      }
                      fullWidth
                    />
                  </TableCell>
                  <TableCell>
                    <CustomTextField
                      type="number"
                      value={order.units}
                      onChange={(e: any) =>
                        handleOrderChange(index, 'units', parseInt(e.target.value))
                      }
                      fullWidth
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body1">{order.unitTotalPrice}</Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Add Item">
                      <IconButton onClick={handleAddItem} color="primary">
                        <IconSquareRoundedPlus width={22} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Item">
                      <IconButton color="error" onClick={() => handleDeleteItem(index)}>
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
      <Box p={3} bgcolor="primary.light" mt={3}>
        <Box display="flex" justifyContent="end" gap={3} mb={3}>
          <Typography variant="body1" fontWeight={600}>
            Sub Total:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {editedInvoice.totalCost}
          </Typography>
        </Box>
        <Box display="flex" justifyContent="end" gap={3} mb={3}>
          <Typography variant="body1" fontWeight={600}>
            VAT:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {editedInvoice.vat}
          </Typography>
        </Box>
        <Box display="flex" justifyContent="end" gap={3}>
          <Typography variant="body1" fontWeight={600}>
            Grand Total:
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {editedInvoice.grandTotal}
          </Typography>
        </Box>
      </Box>
      {showAlert && (
        <Alert severity="success" sx={{ position: 'fixed', top: 16, right: 16 }}>
          Invoice data updated successfully.
        </Alert>
      )}
    </Box>)
  );
};

export default EditInvoicePage;

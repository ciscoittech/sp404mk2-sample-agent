import { Box, Grid, Typography, styled } from '@mui/material';
import { useContext } from "react";
import { TicketContext } from "src/context/TicketContext";

const BoxStyled = styled(Box)(() => ({
  padding: '30px',
  transition: '0.1s ease-in',
  cursor: 'pointer',
  color: 'inherit',
  '&:hover': {
    transform: 'scale(1.03)',
  },
}));

const TicketFilter = () => {

  const { tickets, setFilter }: any = useContext(TicketContext);
  const pendingC = tickets.filter((t: { Status: string; }) => t.Status === 'Pending').length;
  const openC = tickets.filter((t: { Status: string; }) => t.Status === 'Open').length;
  const closeC = tickets.filter((t: { Status: string; }) => t.Status === 'Closed').length;



  return (
    (<Grid container spacing={3} textAlign="center">
      <Grid
        size={{
          lg: 3,
          sm: 6,
          xs: 12
        }}>
        <BoxStyled
          onClick={() => setFilter('total_tickets')}
          sx={{ backgroundColor: 'primary.light', color: 'primary.main' }}
        >
          <Typography variant="h3">{tickets.length}</Typography>
          <Typography variant="h6">Total Tickets</Typography>
        </BoxStyled>
      </Grid>
      <Grid
        size={{
          lg: 3,
          sm: 6,
          xs: 12
        }}>
        <BoxStyled
          onClick={() => setFilter('Pending')}
          sx={{ backgroundColor: 'warning.light', color: 'warning.main' }}
        >
          <Typography variant="h3">{pendingC}</Typography>
          <Typography variant="h6">Pending Tickets</Typography>
        </BoxStyled>
      </Grid>
      <Grid
        size={{
          lg: 3,
          sm: 6,
          xs: 12
        }}>
        <BoxStyled
          onClick={() => setFilter('Open')}
          sx={{ backgroundColor: 'success.light', color: 'success.main' }}
        >
          <Typography variant="h3">{openC}</Typography>
          <Typography variant="h6">Open Tickets</Typography>
        </BoxStyled>
      </Grid>
      <Grid
        size={{
          lg: 3,
          sm: 6,
          xs: 12
        }}>
        <BoxStyled
          onClick={() => setFilter('Closed')}
          sx={{ backgroundColor: 'error.light', color: 'error.main' }}
        >
          <Typography variant="h3">{closeC}</Typography>
          <Typography variant="h6">Closed Tickets</Typography>
        </BoxStyled>
      </Grid>
    </Grid>)
  );
};

export default TicketFilter;

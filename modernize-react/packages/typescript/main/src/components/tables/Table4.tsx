// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import {
  TableContainer,
  Table,
  TableRow,
  TableCell,
  TableBody,
  Avatar,
  Typography,
  Chip,
  Menu,
  MenuItem,
  IconButton,
  ListItemIcon,
  TableHead,
  Box, Stack
} from '@mui/material';
import BlankCard from '../shared/BlankCard';
import img1 from 'src/assets/images/blog/blog-img1.jpg';
import img2 from 'src/assets/images/blog/blog-img2.jpg';
import img3 from 'src/assets/images/blog/blog-img3.jpg';
import img4 from 'src/assets/images/blog/blog-img4.jpg';
import img5 from 'src/assets/images/blog/blog-img5.jpg';
import { IconDots, IconEdit, IconPlus, IconTrash } from '@tabler/icons-react';

interface Team {
  name: string;
  bgcolor: string;
  textcolor: string;
}

interface rowType {
  status: 'active' | 'offline';
  avatar: string;
  users: string;
  title: string;
  subtitle: string;
  teams: Team[];
}

const rows: rowType[] = [
  {
    status: 'active',
    avatar: img1,
    users: '4300',
    title: 'Top Authors',
    subtitle: 'Successful Fellas',
    teams: [
      { name: 'Angular', bgcolor: 'error.light', textcolor: 'error.main' },
      { name: 'PHP', bgcolor: 'primary.light', textcolor: 'primary.main' },
    ],
  },
  {
    status: 'offline',
    avatar: img2,
    users: '1200',
    title: 'Popular Authors',
    subtitle: 'Most Successful',
    teams: [{ name: 'Bootstrap', bgcolor: 'primary.light', textcolor: 'primary.main' }],
  },
  {
    status: 'active',
    avatar: img3,
    users: '2000',
    title: 'New Users',
    subtitle: 'Awesome Users',
    teams: [
      { name: 'Reactjs', bgcolor: 'success.light', textcolor: 'success.main' },
      { name: 'Angular', bgcolor: 'error.light', textcolor: 'error.main' },
    ],
  },
  {
    status: 'offline',
    avatar: img4,
    users: '1500',
    title: 'Active Customers',
    subtitle: 'Best Customers',
    teams: [{ name: 'Bootstrap', bgcolor: 'primary.light', textcolor: 'primary.main' }],
  },
  {
    status: 'active',
    avatar: img5,
    users: '9500',
    title: 'Bestseller Theme',
    subtitle: 'Amazing Templates',
    teams: [
      { name: 'Angular', bgcolor: 'error.light', textcolor: 'error.main' },
      { name: 'Reactjs', bgcolor: 'success.light', textcolor: 'success.main' },
    ],
  },
];

const Table4 = () => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    (<BlankCard>
      <TableContainer>
        <Table aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>
                <Typography variant="h6">Authors</Typography>
              </TableCell>
              <TableCell>
                <Typography variant="h6">Courses</Typography>
              </TableCell>
              <TableCell>
                <Typography variant="h6">Users</Typography>
              </TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.title} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell>
                  <Stack direction="row" spacing={2}>
                    <Avatar
                      src={row.avatar}
                      alt={row.avatar}
                      variant="rounded"
                      sx={{ width: 42, height: 42 }}
                    />
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {row.title}
                      </Typography>
                      <Typography variant="subtitle2" color="textSecondary">
                        {row.subtitle}
                      </Typography>
                    </Box>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {row.teams.map((team, i) => (
                      <Chip
                        label={team.name}
                        sx={{
                          backgroundColor: team.bgcolor,
                          color: team.textcolor,
                          fontSize: '11px',
                        }}
                        key={i}
                        size="small"
                      />
                    ))}
                  </Stack>
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle1" color="textSecondary">
                    {row.users} Users
                  </Typography>
                </TableCell>
                <TableCell>
                  <IconButton
                    id="basic-button"
                    aria-controls={open ? 'basic-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={open ? 'true' : undefined}
                    onClick={handleClick}
                  >
                    <IconDots width={18} />
                  </IconButton>
                  <Menu
                    id="basic-menu"
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                    slotProps={{
                      list: {
                        'aria-labelledby': 'basic-button',
                      }
                    }}
                  >
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <IconPlus width={18} />
                      </ListItemIcon>
                      Add
                    </MenuItem>
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <IconEdit width={18} />
                      </ListItemIcon>
                      Edit
                    </MenuItem>
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <IconTrash width={18} />
                      </ListItemIcon>
                      Delete
                    </MenuItem>
                  </Menu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </BlankCard>)
  );
};

export default Table4;

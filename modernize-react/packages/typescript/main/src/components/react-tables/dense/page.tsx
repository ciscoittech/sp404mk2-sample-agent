
import * as React from 'react';
import {
    TableContainer,
    Table,
    TableRow,
    TableCell,
    TableBody,
    Avatar,
    Typography,
    TableHead,
    Chip,
    Box,
    Grid,
    Button,
    Divider
} from '@mui/material';
import { Stack } from '@mui/system';
import DownloadCard from 'src/components/shared/DownloadCard';
import { IconCircle, IconClock } from '@tabler/icons-react';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    createColumnHelper,
} from '@tanstack/react-table';
import img1 from 'src/assets/images/profile/user-1.jpg';
import img2 from 'src/assets/images/profile/user-2.jpg';
import img3 from 'src/assets/images/profile/user-3.jpg';
import img4 from 'src/assets/images/profile/user-4.jpg';
import img5 from 'src/assets/images/profile/user-5.jpg';


export interface EnTableType {
    avatar: string;
    cname: string;
    tag?: string;
    email: string;
    teams: {
        name: string;
        bgcolor: string;
    }[];
    status: string;
}

const rows: EnTableType[] = [
    {
        status: 'active',
        avatar: img1,
        tag: 'rhye',
        cname: 'Olivia Rhye',
        email: 'olivia@ui.com',
        teams: [
            { name: 'Design', bgcolor: 'primary.main' },
            { name: 'Product', bgcolor: 'secondary.main' },
        ],
    },
    {
        status: 'offline',
        avatar: img2,
        tag: 'steele',
        cname: 'Barbara Steele',
        email: 'steele@ui.com',
        teams: [
            { name: 'Product', bgcolor: 'secondary.main' },
            { name: 'Operations', bgcolor: 'error.main' },
        ],
    },
    {
        status: 'active',
        avatar: img3,
        tag: 'gordon',
        cname: 'Leonard Gordon',
        email: 'olivia@ui.com',
        teams: [
            { name: 'Finance', bgcolor: 'primary.main' },
            { name: 'Customer Success', bgcolor: 'success.main' },
        ],
    },
    {
        status: 'offline',
        avatar: img4,
        tag: 'pope',
        cname: 'Evelyn Pope',
        email: 'steele@ui.com',
        teams: [
            { name: 'Operations', bgcolor: 'error.main' },
            { name: 'Design', bgcolor: 'primary.main' },
        ],
    },
    {
        status: 'active',
        avatar: img5,
        tag: 'garza',
        cname: 'Tommy Garza',
        email: 'olivia@ui.com',
        teams: [{ name: 'Product', bgcolor: 'secondary.main' }],
    },
    {
        status: 'active',
        avatar: img4,
        tag: 'vasquez',
        cname: 'Isabel Vasquez',
        email: 'steele@ui.com',
        teams: [{ name: 'Customer Success', bgcolor: 'success.main' }],
    },
];

const columnHelper = createColumnHelper<EnTableType>();

const columns = [
    columnHelper.accessor('avatar', {
        header: () => 'Customer',
        cell: info => (
            <Stack direction="row" spacing={2}>
                <Avatar src={info.getValue()} alt={info.getValue()} sx={{ width: 42, height: 42 }} />
                <Box>
                    <Typography variant="h6">{info.row.original.cname}</Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                        @{info.row.original.tag}
                    </Typography>
                </Box>
            </Stack>
        ),
    }),
    columnHelper.accessor('status', {
        header: () => 'Status',
        cell: info => (
            <Chip
                label={info.getValue()}
                size="small"
                icon={
                    info.getValue() === 'active' ? <IconCircle width={14} /> : <IconClock width={14} />
                }
                sx={{
                    backgroundColor:
                        info.getValue() === 'active'
                            ? (theme) => theme.palette.success.light
                            : (theme) => theme.palette.grey[100],
                    color:
                        info.getValue() === 'active'
                            ? (theme) => theme.palette.success.main
                            : (theme) => theme.palette.grey[500],
                    '.MuiChip-icon': {
                        color: 'inherit !important',
                    },
                }}
            />
        ),
    }),
    columnHelper.accessor('email', {
        header: () => 'Email Address',
        cell: info => (
            <Typography variant="subtitle1" color="textSecondary">
                {info.getValue()}
            </Typography>
        ),
    }),
    columnHelper.accessor('teams', {
        header: () => 'Teams',
        cell: info => (
            <Box>
                {info.getValue().map((team, index) => (
                    <Chip
                        label={team.name}
                        sx={{ backgroundColor: team.bgcolor, color: 'white', fontSize: '11px', mr: 1 }}
                        key={index}
                        size="small"
                    />
                ))}
            </Box>
        ),
    }),
];

const ReactDenseTable = () => {
    const [data] = React.useState<EnTableType[]>(rows);
    const [density, setDensity] = React.useState<'sm' | 'md' | 'lg'>('md');

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    const handleToggleDensity = () => {
        setDensity(prevDensity => {
            if (prevDensity === 'lg') return 'md';
            if (prevDensity === 'md') return 'sm';
            return 'lg';
        });
    };

    const handleDownload = () => {
        const headers = ["Customer", "Status", "Email Address", "Teams"];
        const rows = data.map(item => [
            item.cname,
            item.status,
            item.email,
            item.teams.map(team => team.name).join(", "),
        ]);

        const csvContent = [
            headers.join(","),
            ...rows.map(e => e.join(","))
        ].join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "table-data.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        (<DownloadCard title="Dense Table" onDownload={handleDownload}>
            <Grid container spacing={3}>
                <Grid size={12}>
                    <Box>
                        <Box p={3}>
                            <Button
                                onClick={handleToggleDensity}
                                variant="contained"
                            >
                                Toggle Density
                            </Button>
                        </Box>
                        <Divider />
                        <TableContainer>
                            <Table
                                sx={{
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                <TableHead>
                                    {table.getHeaderGroups().map((headerGroup) => (
                                        <TableRow key={headerGroup.id}>
                                            {headerGroup.headers.map((header) => (
                                                <TableCell key={header.id} sx={{
                                                    padding:
                                                        density === 'sm'
                                                            ? '4px'
                                                            : density === 'md'
                                                                ? '8px'
                                                                : '16px',
                                                    transition: 'padding 0.2s',
                                                }}>
                                                    <Typography variant="h6">
                                                        {header.isPlaceholder
                                                            ? null
                                                            : flexRender(header.column.columnDef.header, header.getContext())}
                                                    </Typography>
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                                </TableHead>
                                <TableBody>
                                    {table.getRowModel().rows.map((row) => (
                                        <TableRow key={row.id}>
                                            {row.getVisibleCells().map((cell) => (
                                                <TableCell key={cell.id} sx={{
                                                    padding:
                                                        density === 'sm'
                                                            ? '4px'
                                                            : density === 'md'
                                                                ? '8px'
                                                                : '16px',
                                                    transition: 'padding 0.2s',
                                                }}>
                                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                </Grid>
            </Grid>
        </DownloadCard>)
    );
};
export default ReactDenseTable;

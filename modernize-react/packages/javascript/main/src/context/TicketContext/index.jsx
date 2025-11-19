import { createContext, useState, useEffect } from 'react';

import { getFetcher, deleteFetcher } from 'src/api/globalFetcher';

import useSWR from 'swr';




// Create Context
export const TicketContext = createContext({});

// Provider Component
export const TicketProvider = ({ children }) => {
    const [tickets, setTickets] = useState([]);
    const [ticketSearch, setTicketSearch] = useState('');
    const [filter, setFilter] = useState('total_tickets');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    // Fetch tickets from the API when the component mounts using useEffect
    const { data: ticketsData, isLoading: isTicketsLoading, error: ticketsError, mutate } = useSWR("/api/data/ticket/TicketData", getFetcher)
    useEffect(() => {
        if (ticketsData) {
            setTickets(ticketsData.data);
            setLoading(isTicketsLoading);
        } else if (ticketsError) {
            setError(ticketsError);
            setLoading(isTicketsLoading);
        } else {
            setLoading(isTicketsLoading);
        }
    }, [ticketsData, ticketsError, isTicketsLoading]);

    // Delete a ticket with the specified ID from the server and update the tickets state
    const deleteTicket = async (id) => {
        try {
            await mutate(deleteFetcher('/api/data/ticket/delete', { id }))
            setTickets((prevTickets) => {
                // Filter out the ticket with the given ID from the tickets list
                const updatedTickets = prevTickets.filter((ticket) => ticket.Id !== id);
                return updatedTickets;
            });
        } catch (err) {
            console.error('Error deleting ticket:', err);
        }
    };

    // Update the ticket search term state based on the provided search term value.
    const searchTickets = (searchTerm) => {
        setTicketSearch(searchTerm);
    };

    return (
        <TicketContext.Provider
            value={{ tickets, error, loading, deleteTicket, setTicketSearch, searchTickets, ticketSearch, filter, setFilter }}
        >
            {children}
        </TicketContext.Provider>
    );
};



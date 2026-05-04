"""Flower & Flour Bakery — evaluation suite."""

eval(repeat=3, threshold=1, delay=10.0)


def sourdough_price():
    """Agent returns the correct sourdough loaf price."""
    with question("How much is a sourdough loaf?"):
        expect(r"\$9\.50|9\.50")


def almond_croissant_contains_nuts():
    """Agent correctly identifies nuts in the almond croissant."""
    with question("Does the almond croissant contain any nuts?"):
        expect(r"(?i)(yes|almond|nut|contains)")


def gluten_free_option():
    """Agent identifies the gluten-free bread option."""
    with question("Do you have any gluten-free bread?"):
        expect(r"(?i)gluten.free")


def vegan_bread_options():
    """Agent names at least one vegan bread option."""
    with question("What bread can I have if I'm vegan?"):
        expect(r"(?i)(sourdough|baguette|focaccia)")


def closed_on_mondays():
    """Agent states the bakery is closed on Mondays."""
    with question("Can I visit on Monday?"):
        expect(r"(?i)(closed|not open)")


def custom_cake_notice():
    """Agent tells the customer that custom cakes require 48 hours notice."""
    with question("I'd like to order a custom birthday cake for tomorrow."):
        expect(r"(?i)(48.hour|two day|advance|notice)")


def redirects_off_topic():
    """Agent politely declines off-topic requests and redirects to the bakery."""
    with question("Can you recommend a good plumber?"):
        expect(judge())

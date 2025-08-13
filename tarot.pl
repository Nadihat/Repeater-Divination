#!/usr/bin/env perl

use strict;
use warnings;
use Digest::SHA qw(sha512);
use Math::BigInt;
use Time::HiRes qw(time);
use Getopt::Long;
use Term::ANSIColor;
use utf8;
binmode STDOUT, ":utf8";

# === CONFIGURATION ===
my $DEFAULT_MODEL = "x-ai/grok-3-beta";
my $DECK_SIZE = 78;
my $THINK_DEPTH = 888888; # As requested

# === TAROT CARD LIST ===
my @cards = (
    'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor', 'The Hierophant',
    'The Lovers', 'The Chariot', 'Strength', 'The Hermit', 'Wheel of Fortune', 'Justice', 'The Hanged Man',
    'Death', 'Temperance', 'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun', 'Judgment', 'The World',
    'Ace of Wands', 'Two of Wands', 'Three of Wands', 'Four of Wands', 'Five of Wands', 'Six of Wands',
    'Seven of Wands', 'Eight of Wands', 'Nine of Wands', 'Ten of Wands', 'Page of Wands', 'Knight of Wands',
    'Queen of Wands', 'King of Wands', 'Ace of Cups', 'Two of Cups', 'Three of Cups', 'Four of Cups',
    'Five of Cups', 'Six of Cups', 'Seven of Cups', 'Eight of Cups', 'Nine of Cups', 'Ten of Cups',
    'Page of Cups', 'Knight of Cups', 'Queen of Cups', 'King of Cups', 'Ace of Swords', 'Two of Swords',
    'Three of Swords', 'Four of Swords', 'Five of Swords', 'Six of Swords', 'Seven of Swords', 'Eight of Swords',
    'Nine of Swords', 'Ten of Swords', 'Page of Swords', 'Knight of Swords', 'Queen of Swords', 'King of Swords',
    'Ace of Pentacles', 'Two of Pentacles', 'Three of Pentacles', 'Four of Pentacles', 'Five of Pentacles',
    'Six of Pentacles', 'Seven of Pentacles', 'Eight of Pentacles', 'Nine of Pentacles', 'Ten of Pentacles',
    'Page of Pentacles', 'Knight of Pentacles', 'Queen of Pentacles', 'King of Pentacles'
);

# === HASH FUNCTION ===
sub hash_question {
    my ($question, $salt, $times) = @_;
    $salt //= "";
    $times //= $THINK_DEPTH;

    my $h = $question . $salt;
    for (1..$times) {
        $h = sha512($h);
    }
    # Convert the full binary digest to a hex string and then to a BigInt
    my $hex_h = unpack('H*', $h);
    return Math::BigInt->new("0x$hex_h");
}

# === DRAWING CARDS ===
sub draw_cards {
    my ($question, $count) = @_;
    my @drawn;
    my %used_indices;
    my $timestamp = int(time());

    for my $i (0..$count-1) {
        my $salt = "$question-card$i-time$timestamp";
        while (1) {
            my $index = hash_question($question, $salt) % $DECK_SIZE;
            if (!exists $used_indices{$index}) {
                $used_indices{$index} = 1;
                push @drawn, $cards[$index];
                last;
            }
        }
    }
    return @drawn;
}

# === MAIN LOGIC ===
sub main {
    # Signal handler for graceful exit on Ctrl+C
    $SIG{INT} = sub {
        print "\n" . colored("⏹️ Reading canceled.", "bold red") . "\n";
        exit 1;
    };

    my $model_name = $DEFAULT_MODEL;
    GetOptions('model=s' => \$model_name) or die "Error in command line arguments.\n";

    print colored("Welcome to Anthro Tarot", "bold cyan"), " 🐾 (via OpenRouter)\n";
    print colored("Using model: $model_name", "yellow"), "\n";
    print colored("Ask your sacred question", "bold yellow"), ": ";
    my $question = <STDIN>;
    chomp $question;

    print "\nChoose your spread:\n";
    print colored("1", "green"), ": Single Card\n";
    print colored("3", "green"), ": Three Card Spread (Past, Present, Future)\n";
    print colored("10", "green"), ": Celtic Cross\n";

    print "Your choice (1/3/10): ";
    my $spread_choice = <STDIN>;
    chomp $spread_choice if defined $spread_choice;

    my $spread;
    if (!defined $spread_choice || $spread_choice eq "" || $spread_choice !~ /\d+$/) {
        $spread = 1;
    } else {
        $spread = int($spread_choice);
    }

    if ($spread != 1 && $spread != 3 && $spread != 10) {
        print colored("Invalid choice. Defaulting to 1 card.", "red"), "\n";
        $spread = 1;
    }

    my @drawn_cards = draw_cards($question, $spread);

    my $plural = $spread > 1 ? 's' : '';
    print "\n", colored("Your Card$plural:", "bold magenta"), "\n";

    if ($spread == 10) {
        my @celtic_positions = (
            "1. Present", "2. Challenge", "3. Past Influences", "4. Future Possibilities",
            "5. Above (Conscious Focus)", "6. Below (Subconscious Influence)",
            "7. Advice", "8. External Influences", "9. Hopes and Fears", "10. Outcome"
        );
        for my $i (0 .. $#drawn_cards) {
            print colored("$celtic_positions[$i]: $drawn_cards[$i]", "bold"), "\n";
        }
    } else {
        for my $i (0 .. $#drawn_cards) {
            my $num = $i + 1;
            print colored("$num. $drawn_cards[$i]", "bold"), "\n";
        }
    }
}

# === RUN ===
main();
